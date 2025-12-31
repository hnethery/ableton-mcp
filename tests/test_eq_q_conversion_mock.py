
import math

def current_q_to_norm(q):
    normalized_q = q / 10.0
    if normalized_q > 1.0:
        normalized_q = 1.0
    return normalized_q

def proposed_q_to_norm(q):
    # Q range 0.1 to 18.0
    min_q = 0.1
    max_q = 18.0

    if q < min_q: q = min_q
    if q > max_q: q = max_q

    log_min = math.log10(min_q)
    log_max = math.log10(max_q)
    log_q = math.log10(q)

    return (log_q - log_min) / (log_max - log_min)

print(f"{'Q Value':<10} | {'Current Norm':<15} | {'Proposed Norm':<15}")
print("-" * 46)

test_values = [0.1, 0.5, 0.71, 1.0, 2.0, 5.0, 10.0, 15.0, 18.0]

for q in test_values:
    curr = current_q_to_norm(q)
    prop = proposed_q_to_norm(q)
    print(f"{q:<10} | {curr:<15.4f} | {prop:<15.4f}")
