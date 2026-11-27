function [heading_error] = getHeadingEstimationError(lidar_type, perception_stage, d, theta)

% Get the mean and std. dev.
switch lidar_type
    case "OS2-128"
        if perception_stage == "detection"
            D_max = 240;
            mean = 0.6258 + exp( (0.0063 .* d) .^ 2.2688 );
            std = 0.0137 + exp( (0.0082 .* d) .^ 2.3423 );            
        else  % validation
            D_max = 170;
            mean = 0.5632 + exp( (0.0042 .* d) .^ 1.7398 );
            std = 0.1008 + exp( (0.0064 .* d) .^ 1.9705 );  
        end
    case "OS2-64"
        if perception_stage == "detection"
            D_max = 190;
            mean = 1.1403 + exp( (0.0074 .* d) .^ 215.8726 );
            std = 0.6499 + exp( (0.0075 .* d) .^ 125.0842 );
        else  % validation
            D_max = 160;
            mean = 0.5290 + exp( (0.0081 .* d) .^ 1.0384 );
            std = -0.3466 + exp( (0.0097 .* d) .^ 0.4994 );
        end
    case "OS1-64"
        if perception_stage == "detection"
            D_max = 120;
            mean = 0.8533 + exp( (0.0096 .* d) .^ 1.9933 );
            std = -0.2651 + exp( (0.0133 .* d) .^ 0.9798 );
        else  % validation
            D_max = 100;            
            mean = 1.0038 + exp( (0.0133 .* d) .^ 166.8569 );
            std = -0.49 + exp( (0.0174 .* d) .^ 0.6870 );
        end
end

% Make sure that domain is ok
validateInputs(lidar_type, perception_stage, d, theta, D_max);

% Sample values from Gaussian distribution 
heading_error = abs(mean + std * randn());

% Assign a random sign (+1 or -1 with equal probability)
if rand() < 0.5
    heading_error = -heading_error;
end

end