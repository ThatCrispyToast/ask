{
  description = "Flake containing uv && vhs";

  # Flake inputs
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";

  # Flake outputs
  outputs =
    { self, ... }@inputs:

    let
      supportedSystems = [
        "x86_64-linux" # 64-bit Intel/AMD Linux
      ];

      # Helper to provide system-specific attributes
      forEachSupportedSystem =
        f:
        inputs.nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import inputs.nixpkgs { inherit system; };
          }
        );
    in
    {
      devShells = forEachSupportedSystem (
        { pkgs }:
        {
          default = pkgs.mkShellNoCC {
			# Packages
            packages = with pkgs; [
				uv
				vhs
			];

            # Add any shell logic you want executed any time the environment is activated
			shellHook = ''
				if [ ! -d ".venv" ]; then
					echo "Creating virtual environment using uv..."
					uv venv .venv
				fi

				source "./.venv/bin/activate"
				echo "---- Shell Active. -----"
			'';
          };
        }
      );
    };
}
