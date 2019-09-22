{ pkgs, python }:

self: super: {
  "graphene-django" = python.overrideDerivation super."graphene-django" (old: {
    buildInputs = old.buildInputs ++ [ self."pytest-runner" ];
  });

  "pillow" = pkgs.python37Packages.pillow;
}
