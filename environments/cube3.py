from typing import List, Dict, Tuple, Union
import numpy as np
from torch import nn
from random import randrange

from utils.pytorch_models import ResnetModel
from environments.environment_abstract import Environment, State


class Cube3State(State):
    __slots__ = ['colors', 'hash']

    def __init__(self, colors: np.ndarray):
        self.colors: np.ndarray = colors
        self.hash = None

    def __hash__(self):
        if self.hash is None:
            self.hash = hash(self.colors.tostring())

        return self.hash

    def __eq__(self, other):
        return np.array_equal(self.colors, other.colors)


class Cube3(Environment):
    def __init__(self, intermediate_reward_name="uniform", add_actions=False):
        super().__init__()
        self.dtype = np.uint8
        self.cube_len = 3
        self.num_basic_moves = 12

        # solved state
        self.goal_colors: np.ndarray = np.arange(
            0, (self.cube_len ** 2) * 6, 1, dtype=self.dtype)

        # add intermediate states
        # uniform = 1 transition cost per move, TODO
        self.intermediate_reward_name = intermediate_reward_name

        # Dictionaries for corners and edges with their corresponding tiles:
        self.corner_tiles = {
            "WBO": [2,20,44],
            "WBR": [0,26,47],
            "WGO": [8,35,38],
            "WGR": [6,29,53],
            "YBO": [9,18,42],
            "YBR": [11,24,45],
            "YGO": [15,33,36],
            "YGR": [17,27,51],
        }
        self.edge_tiles = {
            "WB": [1,23],
            "WG": [7,32],
            "WO": [5,41],
            "WR": [3,50],
            "YB": [10,21],
            "YG": [16,30],
            "YO": [12,39],
            "YR": [14,48],
            "BO": [19,43],
            "BR": [25,46],
            "GO": [34,37],
            "GR": [28,52],
        }

        self.basic_moves = ['U', 'D', 'L', 'R', 'B', 'F']
        algs = { 
            "edge": ["F1", "F1", "U1", "L1", "R-1", "F1", "F1", "L-1", "R1", "U1", "F1", "F1"],
            "corner": ["R1", "U-1", "L-1", "U1", "R-1", "U-1", "L1", "U1"],
        }
        # Dictionaries for subroutine expansions
        if add_actions:
            self.subroutines = self._expand_subroutines(algs)
        else:
            self.subroutines = []

        #{
        # "<subroutineName>_<face>_<index>_<1/-1>": ["F1", "F1", "U1", "L1", "R-1", "F1", "F1", "L-1", "R1", "U1", "F1", "F1"],
        # edge_f0_r0_1: ["F1", "F1", "U1", "L1", "R-1", "F1", "F1", "L-1", "R1", "U1", "F1", "F1"],
        # ...
        #}

        # Moves are in pairs: (move, -1) followed by (move, 1).
        # 12 basic actions
        self.moves: List[str] = ["%s%i" % (f, n) for f in self.basic_moves for n in [-1, 1]]
        # add subroutines with orientation
        self.moves += [sr for sr in self.subroutines]

        # get idxs changed for moves
        self.rotate_idxs_new: Dict[str, np.ndarray]
        self.rotate_idxs_old: Dict[str, np.ndarray]

        self.adj_faces: Dict[int, np.ndarray]
        self._get_adj()

        self.rotate_idxs_new, self.rotate_idxs_old = self._compute_rotation_idxs(
            self.cube_len, self.moves)

    def next_state(self, states: List[Cube3State], action: int) -> Tuple[List[Cube3State], List[np.float32]]:
        states_np = np.stack([x.colors for x in states], axis=0)
        states_next_np, transition_costs = self._move_np(states_np, action)

        states_next: List[Cube3State] = [Cube3State(x) for x in list(states_next_np)]

        return states_next, transition_costs

    def prev_state(self, states: List[Cube3State], action: int) -> List[Cube3State]:
        move_rev_idx = action + 1 if action % 2 == 0 else action - 1
        return self.next_state(states, move_rev_idx)[0]

    def generate_goal_states(self, num_states: int, np_format: bool = False) -> Union[List[Cube3State], np.ndarray]:
        if np_format:
            goal_np: np.ndarray = np.expand_dims(self.goal_colors.copy(), 0)
            solved_states: np.ndarray = np.repeat(goal_np, num_states, axis=0)
        else:
            solved_states: List[Cube3State] = [Cube3State(self.goal_colors.copy()) for _ in range(num_states)]

        return solved_states

    def is_solved(self, states: List[Cube3State]) -> np.ndarray:
        states_np = np.stack([state.colors for state in states], axis=0)
        is_equal = np.equal(states_np, np.expand_dims(self.goal_colors, 0))

        return np.all(is_equal, axis=1)

    def state_to_nnet_input(self, states: List[Cube3State]) -> List[np.ndarray]:
        states_np = np.stack([state.colors for state in states], axis=0)

        representation_np: np.ndarray = states_np / (self.cube_len ** 2)
        representation_np: np.ndarray = representation_np.astype(self.dtype)

        representation: List[np.ndarray] = [representation_np]

        return representation

    def get_num_moves(self) -> int:
        return len(self.moves)

    def get_nnet_model(self) -> nn.Module:
        state_dim: int = (self.cube_len ** 2) * 6
        nnet = ResnetModel(state_dim, 6, 5000, 1000, 4, 1, True)

        return nnet

    def generate_states(self, num_states: int, backwards_range: Tuple[int, int]) -> Tuple[List[Cube3State], List[int]]:
        """
        Create a list of cube states, for each, scramble them with up to backwards_range[1]+1 moves
        @param num_states create how many cubes
        @param backwards_range (min, max) number of turns to scramble
        """

        assert (num_states > 0)
        assert (backwards_range[0] >= 0)
        assert self.fixed_actions, "Environments without fixed actions must implement their own method"

        # Initialize
        scrambs: List[int] = list(range(backwards_range[0], backwards_range[1] + 1))
        num_env_moves: int = self.get_num_moves()

        # Get goal states (solved cubes)
        states_np: np.ndarray = self.generate_goal_states(num_states, np_format=True)

        # Scrambles
        scramble_nums: np.array = np.random.choice(scrambs, num_states) # how many moves to scramble per cube
        num_back_moves: np.array = np.zeros(num_states) # how many turns have been made currently

        # Go backward from goal state
        moves_lt = num_back_moves < scramble_nums
        while np.any(moves_lt):
            # Get which indices still need to be scrambled further
            idxs: np.ndarray = np.where(moves_lt)[0] 
            # We will only scramble up to len(idxs) / 12 (moves)
            subset_size: int = int(max(len(idxs) / num_env_moves, 1))
            # Pick random indices to scramble
            idxs: np.ndarray = np.random.choice(idxs, subset_size)

            # Select random move from move list
            move: int = randrange(num_env_moves)
            # All idx selected cubes will make this turn
            states_np[idxs], _ = self._move_np(states_np[idxs], move)

            # Update how many turns have been made
            num_back_moves[idxs] = num_back_moves[idxs] + 1
            # Update which cubes still need to be scrambled 
            moves_lt[idxs] = num_back_moves[idxs] < scramble_nums[idxs]

        states: List[Cube3State] = [Cube3State(x) for x in list(states_np)]

        return states, scramble_nums.tolist()

    def expand(self, states: List[State]) -> Tuple[List[List[State]], List[np.ndarray]]:
        assert self.fixed_actions, "Environments without fixed actions must implement their own method"

        # initialize
        num_states: int = len(states)
        num_env_moves: int = self.get_num_moves()

        states_exp: List[List[State]] = [[] for _ in range(len(states))]

        tc: np.ndarray = np.empty([num_states, num_env_moves])

        # numpy states
        states_np: np.ndarray = np.stack([state.colors for state in states])

        # for each move, get next states, transition costs, and if solved
        move_idx: int
        move: int
        for move_idx in range(num_env_moves):
            # next state
            states_next_np: np.ndarray
            tc_move: List[np.float32]
            states_next_np, tc_move = self._move_np(states_np, move_idx)

            # transition cost
            tc[:, move_idx] = np.array(tc_move)

            for idx in range(len(states)):
                states_exp[idx].append(Cube3State(states_next_np[idx]))

        # make lists
        tc_l: List[np.ndarray] = [tc[i] for i in range(num_states)]

        return states_exp, tc_l

    # For fully solved top face, transition = 1-gamma, for completely unsolved top face, transition = 1
    def transition_costs_solvetop(self, states_np: np.ndarray, gamma: int = 0.9) -> np.ndarray:
        corner_names = ["WBO", "WBR", "WGO", "WGR"]
        edge_names = ["WB", "WG", "WO", "WR"]
        # Lists of corners and edges to verify
        corner_tiles_to_check = []
        edge_tiles_to_check = []
        for corner_name in corner_names:
            corner_tiles_to_check += self.corner_tiles[corner_name]
        for edge_name in edge_names:
            edge_tiles_to_check += self.edge_tiles[edge_name]
        corner_is_equal = np.equal(states_np[:, corner_tiles_to_check], np.expand_dims(self.goal_colors[corner_tiles_to_check], 0))
        edge_is_equal = np.equal(states_np[:, edge_tiles_to_check], np.expand_dims(self.goal_colors[edge_tiles_to_check], 0))
        return gamma/2*(np.sum(corner_is_equal, axis=1)/12 + np.sum(edge_is_equal, axis=1)/8)

    def _move_np(self, states_np: np.ndarray, action: int):
        """
        For the cubes in states_np, they turn will turn via action
        Args:
            states_np: cube states to be turned
            action: the turn that all cube states will make
        Returns:
            Return the next state for the cubes
        """
        action_str: str = self.moves[action]

        if action < self.num_basic_moves: # is a basic move
            states_next_np, transition_costs = self._move_np_with_name(states_np, action_str)
        else: # is a subroutine
            steps = self.subroutines[action_str]
            states_next_np = states_np.copy()
            for step in steps:
                states_next_np, transition_costs = self._move_np_with_name(states_next_np, step)

        return states_next_np, transition_costs
    
    def _move_np_with_name(self, states_np: np.ndarray, action_str: str):
        """
        Used by _move_np to get next state with action as a string.
        See _move_np for usage details.
        """
        states_next_np: np.ndarray = states_np.copy()
        # Turn all cubes via the dictionary move function
        # old idx -> new idx per cube
        '''
        e.g. action_str = "U"
        print(self.rotate_idxs_old[action_str])
        print(self.rotate_idxs_new[action_str])
        -
        [ 2  5  8  8  7  6  6  3  0  0  1  2 38 41 44 20 23 26 47 50 53 29 32 35]
        [ 0  1  2  2  5  8  8  7  6  6  3  0 20 23 26 47 50 53 29 32 35 38 41 44]
        '''
        states_next_np[:, self.rotate_idxs_new[action_str]] = states_np[:, self.rotate_idxs_old[action_str]]


        # Transition costs per move
        if self.intermediate_reward_name == "uniform":
            # Transition cost is 1
            transition_costs: List[float] = [1.0]*states_np.shape[0]
        elif self.intermediate_reward_name == "top1":
            # Transition cost based on whether top is solved, trained 3/13
            transition_costs: np.ndarray = 1 + self.transition_costs_solvetop(states_next_np) - self.transition_costs_solvetop(states_np)
        else:
            # Default to transition cost 1
            transition_costs: List[float] = [1.0]*states_np.shape[0]

        return states_next_np, transition_costs

    def _get_adj(self) -> None:
        # WHITE:0, YELLOW:1, BLUE:2, GREEN:3, ORANGE: 4, RED: 5
        self.adj_faces: Dict[int, np.ndarray] = {0: np.array([2, 5, 3, 4]),
                                                 1: np.array([2, 4, 3, 5]),
                                                 2: np.array([0, 4, 1, 5]),
                                                 3: np.array([0, 5, 1, 4]),
                                                 4: np.array([0, 3, 1, 2]),
                                                 5: np.array([0, 2, 1, 3])
                                                 }

    def _compute_rotation_idxs(self, cube_len: int,
                               moves: List[str]) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
        rotate_idxs_new: Dict[str, np.ndarray] = dict()
        rotate_idxs_old: Dict[str, np.ndarray] = dict()

        for move in moves[:self.num_basic_moves]: # edited
            f: str = move[0]
            sign: int = int(move[1:])

            rotate_idxs_new[move] = np.array([], dtype=int)
            rotate_idxs_old[move] = np.array([], dtype=int)

            colors = np.zeros((6, cube_len, cube_len), dtype=int)
            colors_new = np.copy(colors)

            # WHITE:0, YELLOW:1, BLUE:2, GREEN:3, ORANGE: 4, RED: 5

            adj_idxs = {0: {2: [range(0, cube_len), cube_len - 1], 3: [range(0, cube_len), cube_len - 1],
                            4: [range(0, cube_len), cube_len - 1], 5: [range(0, cube_len), cube_len - 1]},
                        1: {2: [range(0, cube_len), 0], 3: [range(0, cube_len), 0], 4: [range(0, cube_len), 0],
                            5: [range(0, cube_len), 0]},
                        2: {0: [0, range(0, cube_len)], 1: [0, range(0, cube_len)],
                            4: [cube_len - 1, range(cube_len - 1, -1, -1)], 5: [0, range(0, cube_len)]},
                        3: {0: [cube_len - 1, range(0, cube_len)], 1: [cube_len - 1, range(0, cube_len)],
                            4: [0, range(cube_len - 1, -1, -1)], 5: [cube_len - 1, range(0, cube_len)]},
                        4: {0: [range(0, cube_len), cube_len - 1], 1: [range(cube_len - 1, -1, -1), 0],
                            2: [0, range(0, cube_len)], 3: [cube_len - 1, range(cube_len - 1, -1, -1)]},
                        5: {0: [range(0, cube_len), 0], 1: [range(cube_len - 1, -1, -1), cube_len - 1],
                            2: [cube_len - 1, range(0, cube_len)], 3: [0, range(cube_len - 1, -1, -1)]}
                        }
            face_dict = {'U': 0, 'D': 1, 'L': 2, 'R': 3, 'B': 4, 'F': 5}
            face = face_dict[f]

            faces_to = self.adj_faces[face]
            if sign == 1:
                faces_from = faces_to[(np.arange(0, len(faces_to)) + 1) % len(faces_to)]
            else:
                faces_from = faces_to[(np.arange(len(faces_to) - 1, len(faces_to) - 1 + len(faces_to))) % len(faces_to)]

            cubes_idxs = [[0, range(0, cube_len)], [range(0, cube_len), cube_len - 1],
                          [cube_len - 1, range(cube_len - 1, -1, -1)], [range(cube_len - 1, -1, -1), 0]]
            cubes_to = np.array([0, 1, 2, 3])
            if sign == 1:
                cubes_from = cubes_to[(np.arange(len(cubes_to) - 1, len(cubes_to) - 1 + len(cubes_to))) % len(cubes_to)]
            else:
                cubes_from = cubes_to[(np.arange(0, len(cubes_to)) + 1) % len(cubes_to)]

            for i in range(4):
                idxs_new = [[idx1, idx2] for idx1 in np.array([cubes_idxs[cubes_to[i]][0]]).flatten() for idx2 in
                            np.array([cubes_idxs[cubes_to[i]][1]]).flatten()]
                idxs_old = [[idx1, idx2] for idx1 in np.array([cubes_idxs[cubes_from[i]][0]]).flatten() for idx2 in
                            np.array([cubes_idxs[cubes_from[i]][1]]).flatten()]
                for idxNew, idxOld in zip(idxs_new, idxs_old):
                    flat_idx_new = np.ravel_multi_index((face, idxNew[0], idxNew[1]), colors_new.shape)
                    flat_idx_old = np.ravel_multi_index((face, idxOld[0], idxOld[1]), colors.shape)
                    rotate_idxs_new[move] = np.concatenate((rotate_idxs_new[move], [flat_idx_new]))
                    rotate_idxs_old[move] = np.concatenate((rotate_idxs_old[move], [flat_idx_old]))

            # Rotate adjacent faces
            face_idxs = adj_idxs[face]
            for i in range(0, len(faces_to)):
                face_to = faces_to[i]
                face_from = faces_from[i]
                idxs_new = [[idx1, idx2] for idx1 in np.array([face_idxs[face_to][0]]).flatten() for idx2 in
                            np.array([face_idxs[face_to][1]]).flatten()]
                idxs_old = [[idx1, idx2] for idx1 in np.array([face_idxs[face_from][0]]).flatten() for idx2 in
                            np.array([face_idxs[face_from][1]]).flatten()]
                for idxNew, idxOld in zip(idxs_new, idxs_old):
                    flat_idx_new = np.ravel_multi_index((face_to, idxNew[0], idxNew[1]), colors_new.shape)
                    flat_idx_old = np.ravel_multi_index((face_from, idxOld[0], idxOld[1]), colors.shape)
                    rotate_idxs_new[move] = np.concatenate((rotate_idxs_new[move], [flat_idx_new]))
                    rotate_idxs_old[move] = np.concatenate((rotate_idxs_old[move], [flat_idx_old]))

        return rotate_idxs_new, rotate_idxs_old
    
    def _expand_subroutines(self, algs):
        """
        Take in a dictionary of algorithms and expand them across 24 cube orientations.
        :param algs: Dictionary of algorithms to expand
            - name_f0_r0_1: [move1, move2, ...]
            - name face rotation
        :return: Expanded dictionary of algorithms
        """
        subroutines = {} # Dictionary of subroutines
        curr_subroutine = {} # Dictionary for current subroutine
        rotations = 4
        faces = 6

        # Time complexity: O(alg * alg_length * 48)

        # Go through each algorithm
        for alg, moves in algs.items():
            for move_str in moves:
                # Get all rotations and faces
                rotated_moves = self._rotate_move(move_str) # rotations
                for j, rot_move in enumerate(rotated_moves):
                    faces = self._face_move(rot_move) # faces
                    for i, face in enumerate(faces):
                        # Add to current subroutine
                        alg_name = f"{alg}_f{i}_r{j}_1"
                        if alg_name in curr_subroutine:
                            curr_subroutine[alg_name].append(face)
                        else:
                            curr_subroutine[alg_name] = [face]
            
            # Get the inverse of all subroutines
            for key, value in curr_subroutine.items():
                inv_routine = key[:-1] + "-1"
                # Inverse the moves, add to final subroutine dictionary
                subroutines[inv_routine] = [self._invert_move(move) for move in value]
            
            # Add current subroutines
            subroutines.update(curr_subroutine)
        
        return subroutines

    def _rotate_move(self, move):
        """
        Map single move to all 4 possible z-axis rotations.
        :param move: Move to rotate
            - U, R, D, L, F, B: Face turns
            - in 90 degree CW increments
        :return: List of rotated moves
        """
        rotations = {
            "U1" : ["U1", "R1", "D1", "L1"],
            "U-1" : ["U-1", "R-1", "D-1", "L-1"],
            "R1" : ["R1", "D1", "L1", "U1"],
            "R-1" : ["R-1", "D-1", "L-1", "U-1"],
            "D1" : ["D1", "L1", "U1", "R1"],
            "D-1" : ["D-1", "L-1", "U-1", "R-1"],
            "L1" : ["L1", "U1", "R1", "D1"],
            "L-1" : ["L-1", "U-1", "R-1", "D-1"],
            # These are the same
            "F1" : ["F1", "F1", "F1", "F1"],
            "F-1" : ["F-1", "F-1", "F-1", "F-1"],
            "B1" : ["B1", "B1", "B1", "B1"],
            "B-1" : ["B-1", "B-1", "B-1", "B-1"]
        }
        return rotations[move]
    
    def _face_move(self, move):
        """
        Map single move to all 6 faces.
        :param move: Move to rotate
            - U, D, L, R, F, B: Face turns
            - Face orientation across y axis rotations 90 CW, then top and bottom
        :return: List of rotated moves
        """
        faces = {
            "U1" : ["U1", "U1", "U1", "U1", "F1", "B1"],
            "U-1" : ["U-1", "U-1", "U-1", "U-1", "F-1", "B-1"],
            "R1" : ["R1", "F1", "L1", "B1", "R1", "R1"],
            "R-1" : ["R-1", "F-1", "L-1", "B-1", "R-1", "R-1"],
            "D1" : ["D1", "D1", "D1", "D1", "B1", "F1"],
            "D-1" : ["D-1", "D-1", "D-1", "D-1", "B-1", "F-1"],
            "L1" : ["L1", "F1", "R1", "B1", "L1", "L1"],
            "L-1" : ["L-1", "F-1", "R-1", "B-1", "L-1", "L-1"],
            "F1" : ["F1", "R1", "B1", "L1", "D1", "U1"],
            "F-1" : ["F-1", "R-1", "B-1", "L-1", "D-1", "U-1"],
            "B1" : ["B1", "L1", "F1", "R1", "U1", "D1"],
            "B-1" : ["B-1", "L-1", "F-1", "R-1", "U-1", "D-1"]
        }
        return faces[move]
    
    def _invert_move(self, move_str):
        """
        Invert a move_str e.g. "U1" -> "U-1"
        :param move_str: Move to invert
        :return: Inverted move
        """
        if len(move_str) == 2:
            return move_str[:-1] + "-1"
        else:
            return move_str[:-2] + "1"
