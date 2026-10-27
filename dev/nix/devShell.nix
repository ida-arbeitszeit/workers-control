{
  mkShell,
  python3,
  nixfmt,
  sqlite,
  glibcLocales,
  includeGlibcLocales,
  lib,
  git,
  bash,
}:
mkShell (
  {
    packages =
      (with python3.pkgs; [
        black
        build
        coverage
        flake8
        isort
        mypy
        packaging
        pip
        psycopg2
        types-setuptools
      ])
      ++ [
        bash
        nixfmt
        sqlite
        git
      ];
    inputsFrom = [ python3.pkgs.workers-control ];
    shellHook = ''
      export PYTHONPATH="$PWD/src:$PYTHONPATH"
    '';
  }
  // lib.optionalAttrs includeGlibcLocales {
    LOCALE_ARCHIVE = "${glibcLocales}/lib/locale/locale-archive";
  }
)
