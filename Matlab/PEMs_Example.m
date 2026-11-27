close all; clear all;

rng('shuffle')

% Select LiDAR type and perception stage
lidar_type = "OS2-128";             % Available inputs: OS2-128, OS2-64, OS1-64
perception_stage = "detection";     % Available inputs: detection or validation

% Set distance and angle of the target object relative to the ego-vehicle's
% right-hand coordinate system (shown below)
distance = 100;      % meters
angle = 0;          % degrees

% ---------------------------------------
%    y ^                     ----------
%      |                     | TARGET |
%   -------                  ----------
%   | EGO | -->               
%   -------   x                         
% ---------------------------------------

% Get detection probability
detection_probability = getObjectDetectionProbability(lidar_type, perception_stage, distance, angle);
object_detected = rand() < detection_probability;   % true with probability p
fprintf("Object detected? %d (1 = yes, 0 = no)\n", object_detected)

% If the object is detected, get position and heading estimation error as
% well as the existence probability
if object_detected
    [x_error, y_error] = getPositionEstimationError(lidar_type, perception_stage, distance, angle);
    [heading_error] = getHeadingEstimationError(lidar_type, perception_stage, distance, angle);
    [existence_prob] = getExistenceProbability(lidar_type, perception_stage, distance, angle);
    fprintf("X error: %.2f m, Y error: %.2f, heading error: %.1f°, existence probability: %.2f\n", x_error, y_error, heading_error, existence_prob)
end

