import itertools
import random, copy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.mines = set()
        self.saves = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return(self.cells)
        else:
            return None
        
        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return(self.cells)
        else:
            return None

        raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        try:
            self.cells.remove(cell)
        except:
            return None
        else:
            self.count-=1



        #raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        try:
            self.cells.remove(cell)
        except:
            return None


        #raise NotImplementedError



class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2) mark the cell as safe
        self.mark_safe(cell)

        # create a set of cells around the Cell
        cells = set()
        for i in range(cell[0]-1,cell[0]+2):
            for j in range(cell[1]-1,cell[1]+2):
                if (i,j) != cell and i in range(0,self.height) and j in range (0,self.width):
                    if ((i,j) not in self.safes):
                        if (i,j) in self.mines:
                            count -= 1
                        else:
                            cells.add((i,j))

        #create new sentence
        new_sentence = Sentence(cells, count)
        
        def Sentance_treatment(sntnce):
            self.knowledge.append(sntnce)

            #create a deep copy of cells we will be iterating over
            new_safes = copy.deepcopy(sntnce.known_safes())
            new_mines = copy.deepcopy(sntnce.known_mines())

            #check for safes and mines in KB
            if new_safes:
                for known_safe in new_safes:
                    self.mark_safe(known_safe)

            if new_mines:
                for known_mine in new_mines:
                    self.mark_mine(known_mine)

            #check for empty sentences in the KB
            for sentence in self.knowledge:
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)

            #check if we can collide any sentences and clean KB of identical sentences
            for sentence_small in self.knowledge:
                for sentence_big in self.knowledge:
                    if (sentence_small!=sentence_big) and sentence_small.cells.issubset(sentence_big.cells):
                        big_cells = copy.deepcopy(sentence_big.cells)
                        small_cells = copy.deepcopy(sentence_small.cells)
                        newest_sentence = Sentence((big_cells - small_cells), (sentence_big.count - sentence_small.count))
                        check = 0
                        for sentence in self.knowledge:
                            if sentence == newest_sentence:
                                check+=1

                        if check > 0:
                            break
                        else:
                            Sentance_treatment(newest_sentence)
       
        Sentance_treatment(new_sentence)

        return None



        raise NotImplementedError

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for killer_move in self.safes:
            if killer_move not in self.moves_made:
                return killer_move
        return None

        raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        for i in range(0,self.width-1):
            for j in range(0, self.height-1):
                if ((i,j) not in self.moves_made) and ((i,j) not in self.mines):
                    return ((i,j))
        
        return None

        raise NotImplementedError
    
#ai = MinesweeperAI()

#ai.add_knowledge((0,0), 3)
#ai.add_knowledge((2,0),3)
#ai.add_knowledge((2,1),3)



