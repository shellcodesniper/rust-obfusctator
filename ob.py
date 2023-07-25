#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NEED PACKAGE: tomllib
import os, toml

PWD = os.path.dirname(os.path.realpath(__file__))
CONFIG = toml.load(os.path.join(PWD, "Cargo.toml"))
def get_name(): return CONFIG["package"]["name"]
def get_version(): return CONFIG["package"]["version"]
def check_lib(): return (True if os.path.exists(os.path.join(PWD, "src/lib.rs")) else False)
def check_bin(): return (True if os.path.exists(os.path.join(PWD, "src/main.rs")) else False)

def get_mod_rs(current_path, module_name):
  mod_rs_path = os.path.join(current_path, module_name, "mod.rs")
  if os.path.exists(mod_rs_path):
    return mod_rs_path
  else:
    mod_rs_path = os.path.join(current_path, module_name + ".rs")
    if os.path.exists(mod_rs_path):
      return mod_rs_path
    else:
      return None

def merge_file(file_path):
  self_bodies = open(file_path).readlines()
  replaced_bodies: list[str] = self_bodies.copy()

  for line_idx, line in enumerate(self_bodies):
    stripped_line = line.strip()
    if stripped_line.count("mod ") == 1 and stripped_line.endswith(";"):
      found_module = stripped_line.split("mod ")[1].split(";")[0].strip();
      module_visibility = stripped_line.split("mod ")[0].strip();
      mod_rs_file = get_mod_rs(os.path.dirname(file_path), found_module)
      if mod_rs_file is not None:
        mod_merged: list[str] = merge_file(mod_rs_file)
        mod_merged_str: str = '\n'.join(mod_merged)
        # print (f"Intenal Module {mod_rs_file} : {mod_merged}")
        replaced_bodies[line_idx] = f"{module_visibility} mod {found_module} {{\n{mod_merged_str}\n}}\n"
  return replaced_bodies

def obfuscate_code(codes: list[str]):
  obfuscated_header = f"// Obfuscated {get_name()} v{get_version()} by {CONFIG['package']['authors'][0]}\n"
  obfuscated_header += "// This file is generated by PY_OBS [[KuuwangE <root@ql.gl>]]\n"
  obfuscated_header += "// DO NOT EDIT THIS FILE\n"
  fmt_bypass = f"// fmt: off\n#![allow(unused_imports)]\n#![allow(unused_variables)]\n#![allow(unused_mut)]#![allow(unused_macros)]\n#![allow(dead_code)]\n#![allow(unused_parens)]\n#![allow(unused_must_use)]\n#![allow(unused_assignments)]\n#![allow(unused_import_braces)]\n#![allow(unused_extern_crates)]\n#![allow(unused_attributes)]\n#![allow(unused_unsafe)]\n"

  replaced_codes = ""
  for code in codes:
    if code.strip().endswith(";"):
      replaced_codes += code.strip()
    else:
      if code.strip().startswith("#![") or code.strip().startswith("#["):
        replaced_codes += code
      else:
        replaced_codes += code.strip()


  wrapped_code = f"{obfuscated_header}\n{fmt_bypass}\n\n{replaced_codes}"
  return wrapped_code

def main():
  is_lib = check_lib()
  is_bin = check_bin()
  if is_lib and is_bin:
    print("Error: can't obfuscate both library and binary.")
    exit(1)

  base_file = os.path.join(PWD, "src/lib.rs") if is_lib else os.path.join(PWD, "src/main.rs")

  output_path = os.path.join("obfuscated", "src", "lib.rs") if is_lib else os.path.join("obfuscated", "src", "main.rs")
  if not os.path.exists(os.path.dirname(output_path)):
    os.makedirs(os.path.dirname(output_path))

  registry_info = CONFIG["package"].get("registry", [])
  registry_info = registry_info[0] if len(registry_info) > 0 else None
  os.system(f"cp Cargo.toml obfuscated/Cargo.toml")
  merged_source = merge_file(base_file)
  merged_source = '\n'.join(merged_source)

  with open(output_path, "wt+") as f:
    f.write(merged_source)

  # NOTE : FORMAT (pretty view)
  os.system(f"cargo fmt -- {output_path}")

  pretty_code: list[str] = open(output_path).readlines()
  converted = obfuscate_code(pretty_code)

  with open(output_path, "wt+") as f:
    f.write(converted)

  if registry_info is not None:
    os.system(f"cargo publish --manifest-path obfuscated/Cargo.toml --registry {registry_info}")
  else:
    os.system(f"cargo publish --manifest-path obfuscated/Cargo.toml")


if __name__ == "__main__":
  main()



