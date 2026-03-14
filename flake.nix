{
  description = "Collection of AI-driven unix-style tools";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
        in
        {
          semgrep = pkgs.python313Packages.buildPythonPackage rec {
            name = "semgrep";
            version = "v0.2.0";
            pyproject = true;

            src = ./semgrep;

            propagatedBuildInputs = [
              pkgs.python313Packages.sentence-transformers
            ];

            meta = with pkgs.lib; {
              description = "Semantic search for local files";
              homepage = "https://github.com/ridulfo/ai-tools/tree/main/semgrep";
              license = licenses.gpl3Plus;
              platforms = platforms.unix;
              mainProgram = "semgrep";
            };
          };
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pkgs.mkShell {
            shellHook = "exec zsh";
            buildInputs = with pkgs; [
              python313Packages.sentence-transformers
            ];
          };
        }
      );
    };
}
