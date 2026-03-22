# Text DAT /project1/train_som - Run Script
# Does NOT use op('script1').module (TD often fails "module compilation" on that).

p = op('/project1/script1').parent()
p.store('som_command', 'train')
op('/project1/script1').cook(force=True)
