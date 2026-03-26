# Text DAT /project1/randomise_data - Run Script
# Does NOT use op('script1').module (TD often fails "module compilation" on that).
# Sets a command on the parent COMP and forces script1 to cook.

p = op('/project1/script1').parent()
p.store('som_command', 'randomise')
op('/project1/script1').cook(force=True)
