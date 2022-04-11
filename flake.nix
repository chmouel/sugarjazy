{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    let out = system:
      let pkgs = nixpkgs.legacyPackages."${system}";
      in
      {

        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python310Packages.poetry
          ];
        };

        defaultPackage = with pkgs.poetry2nix; mkPoetryApplication {
          projectDir = ./.;
          preferWheels = true;
          python = pkgs.python310;
        };

        defaultApp = utils.lib.mkApp {
          drv = self.defaultPackage."${system}";
        };

      }; in with utils.lib; eachSystem defaultSystems out;

}
