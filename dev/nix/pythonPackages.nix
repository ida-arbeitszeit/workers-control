self: super: {
  workers-control = self.callPackage pythonPackages/workers-control.nix { };
  flask-babel = self.callPackage pythonPackages/flask-babel.nix { };
  flask-login = self.callPackage pythonPackages/flask-login.nix { };
}
