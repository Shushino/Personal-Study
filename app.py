import random

# Parameters
trials = 10000  # number of drops

# Toast simulation
jam_down = 0
for _ in range(trials):
    # small random rotation added for "no initial spin"
    rotation = random.uniform(-0.1, 0.1)  # slight wobble
    # heavier side naturally falls down
    rotation += 0.5  # bias for jam side
    if rotation > 0:
        jam_down += 1

# Coin simulation
tails_up = 0
for _ in range(trials):
    if random.random() < 0.5:
        tails_up += 1

# Results
print(f"Toast landed jam-side down: {jam_down/trials*100:.2f}% of the time")
print(f"Coin landed tails up: {tails_up/trials*100:.2f}% of the time")
