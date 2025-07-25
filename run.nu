let path_w = ($env.PWD | str replace --all '\' '/' | str replace 'C:' '/c')
let path_v = [$path_w, ':', $path_w] | str join
docker run -it --rm -v $path_v -w $path_w zupermind/mcdp:2025 bash