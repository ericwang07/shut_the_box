import collections

class Game:
    def __init__(self, args) -> None:        
        self._player_num = 1 if args.one else 2
        self._action_type = "expect" if args.expect else "move"        
        self._prev_score = args.prev_score
        self._roll_sum = args.roll_sum
        self._tiles = args.position        
        self._subset_memo = collections.defaultdict(set)  # dict memo to track all subsets of subsets of S, used for everything        
        self._v_table = {}
        
    def run(self):
        '''
            Function to start the game based on the given  command line arguments. 
            Prints the results of the run based on the action type (calculate expected value
            or find optimal move).
        '''
        
        self._generate_all_subsets([int(c) for c in [1, 2, 3, 4, 5, 6, 7, 8, 9]])                     
        
        if self._player_num == 1:            
            self._player = Player1(tiles=self._tiles, 
                                   action_type=self._action_type,                                   
                                   roll_sum=self._prev_score, # actually roll sum, (4th)
                                   subset_memo=self._subset_memo,
                                   v_table = self._v_table) 
        else:
            self._player = Player2(tiles=self._tiles, 
                                   action_type=self._action_type, 
                                   prev_score=self._prev_score, 
                                   roll_sum=self._roll_sum,
                                   subset_memo=self._subset_memo,
                                   v_table=self._v_table)

        res = self._player.play()
        if type(res) is list:
            print(res)
        else:
            print(f"{res:.6f}")
            
    def _generate_subsets(self, S): # USED ONCE             
        # recursive function that generates all subsets of set S,
        # where each subset is represented as a tuple (S', exS
        # such that S is the subset, exS is S - S'
        subsets = []
        
        visited = []
        excluded = []                
                   
        def dfs(i, sumVisited): # find all subsets of S[i:end]
            # base cases            
            if sumVisited > 45: # restrict the maximum depth to 9!
                return
            if i >= len(S):                  
                subset_tuple = (tuple(visited.copy()), tuple(excluded.copy()))
                subsets.append(subset_tuple)  
                # add the subset to the memo 
                self._subset_memo[(tuple(S), sumVisited)].add(subset_tuple)
                return                             
            # recursive step            
            visited.append(S[i]) # include i-th element            
            dfs(i+1, sumVisited + S[i])
            x = visited.pop() # exclude i-th element
            excluded.append(x)            
            dfs(i+1, sumVisited)
            excluded.pop()
            return
        
        dfs(0, 0)   
        return subsets 

    def _generate_all_subsets(self, S):
        '''
            Generates the power set for each subset S' of S, storing the results in a dict
            where key = (S', r) and value is a list of subset tuples of S' where its sum is equal
            to r. 
        '''
        subsets_triples = self._generate_subsets(S)
        for subset, excluded in subsets_triples:                                    
            self._generate_subsets(subset)            
        return

class Player:
    def __init__(self, tiles, action_type, subset_memo, v_table, prev_score=0, roll_sum=0) -> None:
        self._tiles = [int(c) for c in tiles] # convert the string to a list of ints
        # have the player hold onto action type so player 2 can output expected value for player1 optimal move
        self._action_type = action_type
        self._prev_score = prev_score # None if Player is Player1
        self._roll_sum = roll_sum # None if action type is expect and not move
        self._two_dice_prob = {2 : 1./36,
                               3 : 2./36,
                               4 : 3./36,
                               5 : 4./36,
                               6 : 5./36,
                               7 : 6./36,
                               8 : 5./36,
                               9 : 4./36,
                               10 : 3./36,
                               11 : 2./36,
                               12 : 1./36}       
        # use a subset memo where key = (S, r) and value is a subset representation of S in which
        # the sum of its members are equal to r.
        self._subset_memo = subset_memo 
        self._v_table = v_table
        
    def play(self): # return expected value or optimal move 
        '''
            Initiate the game from the given player. Returns the expected value or optimal move based on
            the given action type.
        '''               
        if self._action_type == "expect":                                                           
            v = self._expected_value(S=self._tiles, r=None)            
            return v                        
        else:
            m = self._optimal_move(r=self._roll_sum)
            return m
    
    def _expected_value(self):
        '''
            Abstract class for calculating the expected value of the given start state.
            Player1 and Player2 child classes implement this.
        '''
        pass
    
    def _optimal_move(self, r):                
        '''
            Calculates the optimal move based on a given roll sum. Works for both
            Player1 and Player2.
        '''
        actions = self._subset_memo[(tuple(self._tiles), r)]
        
        # if there doesn't exist a valid "move" return no move
        if not actions:
            return []
        
        max_v = 0.0
        best_move = None
        for action in actions:     
            subset, excluded = action              
            # if there is exists a valid "move"
            curr_v = self._expected_value(S=excluded)
            if curr_v > max_v: # If the current move is better, remember the move and its value
                max_v = max(max_v, curr_v)
                best_move = subset

        return list(best_move) # else, return the best move
            
class Player1(Player):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)  
        
    def _expected_value(self, S, r=None): 
        total_sum = sum(S)
        t = self._prev_score        
        
        if (tuple(S), r, t) in self._v_table:                           
            return self._v_table[(tuple(S), r, t)]
        
        if not r: # stochastic state
            # terminal state
            if not S: # if there are no tiles to close
                self._v_table[(tuple(S), r, t)] = 1.0
                return self._v_table[(tuple(S), r, t)]
            
            # calculate the expected value
            v_sum = 0.0
            # case 1: 2 dice roll            
            if total_sum > 6:                
                for roll in range(2, 13):
                    # probability of rolling sum roll
                    p = self._two_dice_prob[roll] 
                    v = p * self._expected_value(S=S, r=roll)
                    v_sum += v 
            # case 2: 1 die roll
            elif 0 <= total_sum <= 6:                             
                p = 1./6 # one die probability (same for all sums)
                for roll in range(1, 7):                    
                    v = p * self._expected_value(S=S, r=roll)
                    v_sum += v
                                
            self._v_table[(tuple(S), r, t)] = v_sum
            return self._v_table[(tuple(S), r, t)]
        
        else: # choose state (r is provided)                                   
            actions = self._subset_memo[(tuple(S), r)]                                                                                  
            # if p1 can't close any more tiles
            if not actions:
                # create a second player
                opponent = Player2(tiles=[i for i in range(1, 10)],
                                   action_type="expect",
                                   prev_score=total_sum,                                   
                                   subset_memo=self._subset_memo,
                                   v_table=self._v_table) # P1's score is the score P2 is trying to beat                
                p2_v = opponent.play()                
                
                self._v_table[(tuple(S), r, t)] = 1.0 - p2_v
                return self._v_table[(tuple(S), r, t)]
            
            max_v = 0.0
            for action in actions:                
                subset, excluded = action                        
                v_next = self._expected_value(S=excluded, r=None) # cut down S
                max_v = max(max_v, v_next)                                            
            self._v_table[(tuple(S), r, t)] = max_v 
            
            return self._v_table[(tuple(S), r, t)]
    
class Player2(Player):
    def __init__(self, *args, **kwargs) -> None:        
        super().__init__(*args, **kwargs)

    def _expected_value(self, S, r=None):        
        # expected P1 wins starting turn with tiles 𝑆
        total_sum = sum(S)
        t = self._prev_score
        
        if (tuple(S), r, t) in self._v_table:                 
            return self._v_table[(tuple(S), r, t)]        
        
        if not r: # stochastic state                                    
            # terminal state
            if total_sum < t:                
                self._v_table[(tuple(S), r, t)] = 1.0
                return self._v_table[(tuple(S), r, t)]
            
            # calculate the expected value
            v_arr = []
            # case 1: 2 dice roll
            if total_sum >= max(7, t):                
                for roll in range(2, 13):
                    # probability of rolling sum roll
                    p = self._two_dice_prob[roll] 
                    v = p * self._expected_value(S=S, r=roll)
                    v_arr.append(v)  
            # case 2: 1 die roll
            elif min(0, t) <= total_sum <= 6:                             
                p = 1./6 # one die probability (same for all sums)
                for roll in range(1, 7):                    
                    v = p * self._expected_value(S=S, r=roll)
                    v_arr.append(v)
      
            self._v_table[(tuple(S), r, t)] = sum(v_arr)
            return self._v_table[(tuple(S), r, t)]
        
        else: # choose state (r is provided)      
            # if the best action for the given state is known 
                
            actions = self._subset_memo[(tuple(S), r)]            
            # if there doesn't exist a valid "play", compare scores with p2
            if not actions:
                if total_sum == t:                      
                    self._v_table[(tuple(S), r, t)] = 0.5                 
                    return self._v_table[(tuple(S), r, t)]
                if total_sum > t:                      
                    self._v_table[(tuple(S), r, t)] = 0.0
                    return self._v_table[(tuple(S), r, t)]                         
            
            max_v = 0.0
            best_action = None
            for action in actions:                          
                subset, excluded = action                
                v_next = self._expected_value(S=excluded)
                max_v = max(max_v, v_next)
                best_action = action
            
            self._v_table[(tuple(S), r, t)] = max_v                      
            return self._v_table[(tuple(S), r, t)]
        

                        
        



                
                    
                
            
            
                    
                
