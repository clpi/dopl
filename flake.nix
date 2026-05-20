{
  description = "Ado - A Minimal Programming Language";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        packages = rec {
          default = ado;
          ado = pkgs.stdenv.mkDerivation {
            pname = "ado";
            version = "unstable";
            src = ./.;

            buildInputs = [ pkgs.gcc ];

            makeFlags = [ "PREFIX=$(out)" ];

            doCheck = true;
            checkTarget = "test";

            meta = with pkgs.lib; {
              description = "Ado - A Minimal Programming Language";
              homepage = "https://github.com/ado-lang/ado";
              license = licenses.mit;
              maintainers = [ ];
            };
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            gcc
            gnumake
          ];
        };
      }
    );
}
