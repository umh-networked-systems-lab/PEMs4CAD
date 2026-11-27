function [existence_prob] = getExistenceProbability(lidar_type, perception_stage, d, theta)

% Get the mean and std. dev.
switch lidar_type
    case "OS2-128"
        if perception_stage == "detection"
            D_max = 240;
            mean = -0.0020 .* d + 0.8016;
            std = 0 .* d + 0.0667;            
        else  % validation
            D_max = 170;
            mean = -0.0016 .* d + 0.8403;
            std = 0.0003 .* d + 0.0371;  
        end
    case "OS2-64"
        if perception_stage == "detection"
            D_max = 190;            
            mean = -0.0031 .* d + 0.8410;
            std = 0.0011 .* d - 0.0396;
        else  % validation
            D_max = 160;            
            mean = -0.0021 .* d + 0.8096;
            std = 0.0006 .* d + 0.0232;
        end
    case "OS1-64"
        if perception_stage == "detection"
            D_max = 120;            
            mean = -0.0052 .* d + 0.8484;
            std = 0.0008 .* d + 0.0232;
        else  % validation
            D_max = 100;                        
            mean = -0.0058 .* d + 0.8607;
            std = 0.0007 .* d + 0.0242;
        end
end

% Make sure that domain is ok
validateInputs(lidar_type, perception_stage, d, theta, D_max);

% Sample values from Gaussian distribution 
existence_prob = min(abs(mean + std * randn()), 1);

end