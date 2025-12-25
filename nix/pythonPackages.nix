self: super: {
  arbeitszeitapp = self.callPackage pythonPackages/arbeitszeitapp.nix { };
  flask-babel = self.callPackage pythonPackages/flask-babel.nix { };
  flask-login = self.callPackage pythonPackages/flask-login.nix { };
  flask-restx = self.callPackage pythonPackages/flask-restx.nix { };
}
