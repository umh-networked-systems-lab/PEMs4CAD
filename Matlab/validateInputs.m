function validateInputs(lidar_type, perception_stage, d, theta, D_max)
%VALIDATEINPUTS Validate lidar type, perception stage and (d, theta) domain.
%   d     : distance in meters (scalar or array)
%   theta : angle in degrees (scalar or array, same size as d)
if nargin < 5
    error("validateInputs:missingInput", ...
        "D_max must be provided as the fifth input.");
end
if ~isnumeric(D_max) || ~isscalar(D_max) || ~isreal(D_max) ...
        || ~isfinite(D_max) || D_max <= 0
    error("validateInputs:badDmax", ...
        "D_max must be a positive, finite, real scalar.");
end

%% 1) lidar_type
switch lidar_type
    case {"OS2-128", "OS2-64", "OS1-64"}
        % supported, continue
    otherwise
        error("validateInputs:notSupported", ...
            "Lidar type '%s': not supported.", lidar_type);
end

%% 2) perception_stage
if ~any(perception_stage == ["detection", "validation"])
    error("validateInputs:badStage", ...
        "perception_stage must be 'detection' or 'validation' (got '%s').", ...
        perception_stage);
end

%% 3) d and theta
if ~isnumeric(d) || ~isnumeric(theta) || ~isreal(d) || ~isreal(theta) ...
        || any(~isfinite(d(:))) || any(~isfinite(theta(:)))
    error("validateInputs:badNumeric", ...
        "d and theta must be real, finite numeric values.");
end
if ~isscalar(d) && ~isscalar(theta) && ~isequal(size(d), size(theta))
    error("validateInputs:sizeMismatch", ...
        "d and theta must be the same size (or one of them scalar).");
end
if any(d(:) < 0)
    error("validateInputs:negativeD", "d must be non-negative.");
end

% Fold the angle into [0, 180)
th = mod(theta, 180);

% Domain limit D_lim(theta)
D_lim = 20 * ones(size(th));                       % [45, 135)
D_lim(th >= 15 & th < 45  | th >= 135 & th < 165) = 50;   % [15,45) U [135,165)
D_lim(th <  15 | th >= 165)                       = D_max; % [0,15) U [165,180)

outOfDomain = d > D_lim;   % implicit expansion handles scalar/array mix
if any(outOfDomain(:))
    error("validateInputs:outOfDomain", ...
        "d exceeds the allowed domain D_lim(theta).");
end


end