class Buy:
    BALL_DICTIONARY = {
        1: {"name": "Pokeball", "price": 200, "percentage_buy": 40 },
        2: {"name": "Greatball", "price": 500, "percentage_buy": 45 },
        3: {"name": "Ultraball", "price": 1500, "percentage_buy": 10 },
        4: {"name": "Masterball", "price": 100000, "percentage_buy": 80 }
    }

    @staticmethod
    def generate_purchase_commands(budget):
        commands = []
        if budget > 2500:
            # The order of priority
            priority_order = [1, 2, 3, 4]

            # Reverse the priority order
            priority_order = priority_order[::-1]
            for id in priority_order:
                ball = Buy.BALL_DICTIONARY[id]
                percentage = ball["percentage_buy"]
                #Calculate the percentage of budget for this iteration
                percentage_of_budget = budget * (percentage / 100)
                
                balls_to_buy = int(percentage_of_budget / ball["price"])
                
                budget -= balls_to_buy * ball["price"]
                if balls_to_buy > 0:
                    commands.append(f";shop buy {id} {balls_to_buy}") 
        return commands
    