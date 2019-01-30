class node_c:
    # player: -- maybe not just str
    #   we need structured data to encode choice

    def __init__ (self, player, state):
        self.player = player
        self.state = state

class extensive_form_c:
    def __init__ (self, choose):
        # choice: -- not just str
        #   we need structured data to encode choice

        # choose: (node, choice) -> node
        self.choose = choose

        # pure_utility: leaf -> payoff_series

        # get_choice_list: node -> choice_stream

# backward induction
# minmax
