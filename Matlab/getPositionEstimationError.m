function [x_error, y_error] = getPositionEstimationError(lidar_type, perception_stage, d, theta)

% Get the mean and std. dev.
switch lidar_type
    case "OS2-128"
        if perception_stage == "detection"
            D_max = 240;
            x_mean = -0.71 + exp( (0.0051 .* d) .^ 10);
            x_std = -0.9137 + exp( (0.004486 .* d) .^ (6.108));
            y_mean = 0.0005 .* d + 0.0335;
            y_std = 0 .* d + 0.0988;
        else  % validation
            D_max = 170;
            x_mean = 0 .* d + 0.3; 
            x_std = 0 .* d + 0.0871;          
            y_mean = 0.0005 .* d + 0.0318;
            y_std = 0.0008 .* d + 0.0296;
        end
    case "OS2-64"
        if perception_stage == "detection"
            D_max = 190;
            x_mean = -0.3164 + exp( (0.0012 .* d) .^ 1.3490 );
            x_std = -0.8982 + exp( (0.0071 .* d) .^ 23.8104 );
            y_mean = 0.0008 .* d + 0.0129; 
            y_std = 0.0015 .* d + -0.0103;
        else  % validation
            D_max = 160;
            x_mean = -0.0003 .* d + 0.7027;
            x_std = 0.0002 .* d + 0.0876;
            y_mean = 0.0008 .* d + 0.0123;
            y_std = 0.0009 .* d + 0.0188;        
        end
    case "OS1-64"
        if perception_stage == "detection"
            D_max = 120;
            x_mean = -0.2972 + exp( (0.0012 .* d) .^ 15.8399 );
            x_std = -0.9369 + exp( (0.0017 .* d) .^ 1.3642 );
            y_mean = 0.0009 .* d + 0.0136;
            y_std = 0.0015 .* d + 0.0050;
        else  % validation
            D_max = 100;
            x_mean = 0.0017 .* d + 0.6516; 
            x_std = -0.0003 .* d + 0.0868;
            y_mean = 0.0010 .* d + 0.0120;
            y_std = 0.0008 .* d + 0.0237;
        end
end

% Make sure that domain is ok
validateInputs(lidar_type, perception_stage, d, theta, D_max);

% Sample values from Gaussian distribution 
x_error = abs(x_mean + x_std * randn());
y_error = abs(y_mean + y_std * randn());

% Assign a random sign (+1 or -1 with equal probability)
if rand() < 0.5
    x_error = -x_error;
end
if rand() < 0.5
    y_error = -y_error;
end

end