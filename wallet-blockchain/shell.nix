{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.flask
    pkgs.python311Packages.requests
  ];

  shellHook = ''
    # Set up Python environment
    export PYTHONPATH=`pwd`:$PYTHONPATH
    export FLASK_APP=app.py
    export FLASK_ENV=development
    
    echo "Environment ready!"
    echo "Run 'flask run' to start the API server"
  '';
}
