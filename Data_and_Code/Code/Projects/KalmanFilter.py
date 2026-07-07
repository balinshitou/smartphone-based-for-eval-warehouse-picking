def OneDKalmanFilter(initial_value, initial_probability, measurement_value, initial_process_variance, initial_measurement_variance):
    optimal_estimation = []
    prior_estimation = initial_value
    prior_probability = initial_probability + initial_process_variance
    for cycle_count in range(len(measurement_value)):
        Kalman_gain = prior_probability / (prior_probability + initial_measurement_variance)
        optimal_estimation_value = prior_estimation + Kalman_gain * (measurement_value[cycle_count] - prior_estimation)
        optimal_estimation.append(optimal_estimation_value)
        optimal_probability = (1 - Kalman_gain) * prior_probability
        prior_probability = optimal_probability + initial_process_variance
        prior_estimation = optimal_estimation_value
    return optimal_estimation