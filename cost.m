function [J grad] = cost(params, layer_sizes, dim, input_pos, X, Y, lambda, mu)

index = 1;
Theta = {};
for i = 1:length(layer_sizes) - 1
    next_index = index + layer_sizes(i + 1) * (layer_sizes(i) + 1);
    Theta{i} = reshape(params(index:next_index - 1), layer_sizes(i + 1), layer_sizes(i) + 1);
    index = next_index;
end;

pos = {};
pos_grad = {};
pos_count = 0;
if layer_sizes(1) == size(input_pos, 1)
    start_index = 2;
    pos{1} = input_pos;
elseif length(input_pos)
    error('mismatching input_pos');
else
    start_index = 1;
end;
for i = start_index:length(layer_sizes)
    next_index = index + layer_sizes(i) * dim;
    pos{i} = reshape(params(index:next_index - 1), layer_sizes(i), dim);
    index = next_index;
    pos_count += layer_sizes(i) * dim;
end;

m = size(X, 1);

J = 0;

a = {};
delta = {};
Delta = {};
for i = 1:length(layer_sizes) - 1
    Delta{i} = zeros(size(Theta{i}));
end;
for i = 1:m
    a{1} = X(i, :)';
    for j = 1:length(layer_sizes) - 1
        a{j + 1} = sigmoid(Theta{j} * [1; a{j}]);
    end;
    J += (-Y(i, :) * log(a{end}) - (1 - Y(i, :)) * log(1 - a{end})) / m;
    delta{length(layer_sizes)} = a{end} - Y(i, :)';
    for j = length(layer_sizes) - 1:-1:2
        g = [1; a{j}];
        delta{j} = Theta{j}' * delta{j + 1} .* (g .* (1 - g));
        delta{j} = delta{j}(2:end);
    end;
    for j = 1:length(layer_sizes) - 1
        Delta{j} += delta{j + 1} * [1; a{j}]';
    end;
end;

% Normalize to get gradients
for i = 1:length(layer_sizes) - 1
    Delta{i} /= m;
end;

for i = 1:length(layer_sizes)
    pos_grad{i} = zeros(layer_sizes(i), dim);
end;

connection_cost = 0;
crowd_cost = 0;
for i = 1:length(layer_sizes) - 1
    for j = 1:layer_sizes(i)
        for k = 1:layer_sizes(i + 1)
            dif = pos{i}(j, :) - pos{i + 1}(k, :);
            dist = dif * dif';
            theta = Theta{i}(k, j + 1);
            connection_cost += 0.5 * dist * theta ^ 2;
            Delta{i}(k, j + 1) += lambda * dist * theta;
            crowd_cost += 0.5 / dist;
            temp = (lambda * theta ^ 2 - mu / dist ^ 2);
            pos_grad{i}(j, :) += dif * temp;
            pos_grad{i +1}(k, :) -= dif * temp;
        end;
    end;
end;

J += lambda * connection_cost + mu * crowd_cost;

grad = [];
for i = 1:length(layer_sizes) - 1
    grad = [grad; Delta{i}(:)];
end;
for i = start_index:length(layer_sizes)
    grad = [grad; pos_grad{i}(:)];
end;

% Full crowd cost disabled
if 0
    pos_flat = [];
    for i = 1:length(layer_sizes)
        pos_flat = [pos_flat; pos{i}];
    end;

    crowd_cost = 0;
    for i = 1:size(pos_flat, 1)
        for j = i+1:size(pos_flat, 1)
            dif = pos_flat(i, :) - pos_flat(j, :);
            dist = dif * dif';
            crowd_cost += 1 / dist;
        end;
    end;

    J += mu * crowd_cost;
end;

