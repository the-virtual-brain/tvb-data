
%% Load TVB face from obj, convert ot bst format
% After, it was imported to bst then aligned MANUALLY. This is done ONCE
% already, no need to do it again, these are just notes.
%
face = loadawobj('obj/face_surface.obj');
figure
f3 = [face.f4(1:3, :) [face.f4(3:4, :); face.f4(1, :)]]';
h = patch('vertices', face.v', 'faces', f3);
h.FaceAlpha = 0.5;
axis equal
rotate3d
%%
face_bst = [];
face_bst.Vertices = bsxfun(@minus, face.v', mean(face.v')) * 1e-3;
face_bst.Faces = f3;
face_bst.Comment = 'tvb face surface';


%% verify Brainstorm data visually
%
% 1) load the TVB protocol in Brainstorm
% 2) export tvb-cortex_reg13 to MATLAB variable "cortex"
% 3) idem. for inner_skull, outer_skull, bem_head -> scalp and face
% 4) export meg seeg eeg sensors to MATLAB
% 5) verify all positions visually before writing files

figure(1)
clf
scl = 1e3;
O = mean(cortex.Vertices * scl);

surfaces = {cortex, inner_skull, outer_skull, scalp, face};
colors = parula(length(surfaces));
for i=1:length(surfaces)
    s = surfaces{i};
    h = patch('vertices', bsxfun(@minus, s.Vertices * scl, O), 'faces', s.Faces);
    h.FaceAlpha = 0.2;
    h.EdgeColor = colors(i, :);
    h.EdgeAlpha = 0.2;
    hold on
end

chans = reshape({eeg 'EEG' meg 'MEG' seeg 'SEEG'}, 2, 3)';
colors = 'rgb';
for i=1:size(chans, 1)
    tm = strcmp({chans{i, 1}.Channel.Type}, chans{i, 2});
    loc = [chans{i, 1}.Channel(tm).Loc]';
    if strcmp(chans{i, 2}, 'MEG')
        loc = squeeze(mean(reshape(loc, 4, [], 3), 1));
    end
    loc = bsxfun(@minus, loc * scl, O);
    plot3(loc(:, 1), loc(:, 2), loc(:, 3), [colors(i) 'o']);
    fprintf('%d %s sensors', sum(tm), chans{i, 2});
end

grid on
axis equal
rotate3d

xlabel('X+ Right (m)')
ylabel('Y+ Anterior (m)')
zlabel('Z+ Superior (m)')

title('TVB Forward Model')


%% save new surface
surfaces = {'inner_skull' inner_skull; 'outer_skull' outer_skull; 'scalp' scalp; 'face' face; 'cortex' cortex};

for i=1:size(surfaces, 1)
    surfi = surfaces{i, 2};
    surf_name = sprintf('%s_%d', surfaces{i, 1}, size(surfi.Vertices, 1));
    surf_path = fullfile('surfaceData', surf_name);
    mkdir(surf_path) 
    files = cellfun(@(s) [s '.txt'], {'vertices' 'vertex_normals' 'triangles'}, 'UniformOutput', false);
    fullfiles = cellfun(@(s) fullfile(surf_path, s), files, 'UniformOutput', false);
    fprintf(fopen(fullfiles{1}, 'w'), '%f %f %f\n', bsxfun(@minus, surfi.Vertices' * 1e3, O'));
    fprintf(fopen(fullfiles{2}, 'w'), '%f %f %f\n', surfi.VertNormals');
    fprintf(fopen(fullfiles{3}, 'w'), '%d %d %d\n', surfi.Faces' - 1);
    fclose all;
    here = cd(surf_path);
    zip(['../' surf_name], files);
    cd(here);
    rmdir(surf_path, 's')
    fprintf('generated surfaceData/%s.zip\n', surf_name);
end

%%  & sensor files
for i=1:size(chans, 1)
    tm = strcmp({chans{i, 1}.Channel.Type}, chans{i, 2});
    names = {chans{i, 1}.Channel(tm).Name};
    loc = [chans{i, 1}.Channel(tm).Loc]';
    if strcmp(chans{i, 2}, 'MEG')
        loc = squeeze(mean(reshape(loc, 4, [], 3), 1));
        ori = [chans{i, 1}.Channel(tm).Orient]';
        loc = [loc ori(1:4:end, :)];
    end
    loc(:, 1:3) = bsxfun(@minus, loc(:, 1:3) * 1e3, O);
    fd = fopen(fullfile('sensors', sprintf('%s_%d.txt', chans{i, 2}, size(loc, 1))), 'w');
    for i=1:size(loc, 1)
        fprintf(fd, '%s\t', names{i});
        fprintf(fd, '%f\t', loc(i, :));
        fprintf(fd, '\n');
    end
    fclose(fd);
end


%% save new centers & orientations files for each region mapping
region_mappings = {'16k_76' '16k_192'};
for i=1:length(region_mappings)
    
    %% load region mapping
    rmap = load(fullfile('regionMapping', ['regionMapping_' region_mappings{i} '.txt'])) + 1;
    ru = unique(rmap);
    if length(rmap) > size(cortex.Vertices, 1)
        rmap = rmap(1:size(cortex.Vertices, 1));
    end
    
    %% unzip, load centers & orientations
    parts = strsplit(region_mappings{i}, '_');
    conn_name = ['connectivity_' parts{2}];
    conn_path = fullfile('connectivity', conn_name);
    unzip([conn_path  '.zip'], 'connectivity');
    fd = fopen(fullfile(conn_path, 'centres.txt'), 'r');
    parts = textscan(fd, '%s %f %f %f\n');
    c_names = parts{1};
    fclose(fd);
    
    %% compute new cneters & orientations
    centers = zeros(length(ru), 3);
    ori = zeros(length(ru), 3);
    for j=1:length(ru)
        rm = find(ru(j) == rmap);
        centers(j, :) = mean(cortex.Vertices(rm, :));
        ori(j, :) = mean(cortex.VertNormals(rm, :));
    end
    centers(isnan(centers(:, 1)), :) = 0.0;
    ori(isnan(ori(:, 1)), :) = 0.0;
    
    %% write back to connectivity
    fd = fopen(fullfile(conn_path, 'centres.txt'), 'w');
    for j=1:size(centers, 1)
        fprintf(fd, '%s %f %f %f\n', c_names{j}, centers(j, :) * 1e3 - O);
    end
    fclose(fd);
    save(fullfile(conn_path, 'average_orientations.txt'), '-ascii', 'ori');
    
    %% zip up
    cd connectivity
    zip(conn_name, conn_name);
    rmdir(conn_name, 's');
    cd ..
    
end