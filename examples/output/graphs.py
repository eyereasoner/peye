t('bob', 'child_of', 'alice')
t('carol', 'child_of', 'alice')
allowed('carol')
children('alice', ['bob', 'carol'])
