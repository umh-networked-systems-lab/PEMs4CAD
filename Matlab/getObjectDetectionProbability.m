function [prob] = getObjectDetectionProbability(lidar_type, perception_stage, d, theta)

% Check that inputs are valid
D_max = 250; % meters
validateInputs(lidar_type, perception_stage, d, theta, D_max);

% Get the object detection probability
switch lidar_type
    case "OS2-128"
        if perception_stage == "detection"
            prob = exp(-(0.0057 .* d) .^ 7.05);  
        else  % validation
            prob = exp(-(0.0081 .* d) .^ 9.65);  
        end
    case "OS2-64"
        if perception_stage == "detection"
            prob = exp(-(0.0079 .* d) .^ 6.05);    
        else  % validation
            prob = exp(-(0.0113 .* d) .^ 6.1);    
        end
    case "OS1-64"
        if perception_stage == "detection"
            prob = exp(-(0.0145 .* d) .^ 7.1);    
        else  % validation
            prob = exp(-(0.018 .* d) .^ 4.8);    
        end
        
end