found(triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en'))))
witness(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))]), 'sk_0')

clause(1, fact(quoted(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))]))))
clause(2, fact(member_of(X, [X, *__anon0])))
clause(4, backward(includes(graph(Triples), Triple), member_of(Triple, Triples)))
clause(5, forward(found(T), quoted(G), includes(G, T)))
clause(6, forward(witness(X, W), quoted(X)))

step(found(triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))), clause(5), {'T': triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en'))), 'G': graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))])}, [quoted(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))])), includes(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))]), triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en'))))])
step(quoted(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))])), clause(1), {}, [])
step(includes(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))]), triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))), clause(4), {'Triples': [triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))], 'Triple': triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))}, [member_of(triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en'))), [triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))])])
step(member_of(triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en'))), [triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))]), clause(2), {'X': triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en'))), '__anon0': []}, [])
step(witness(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))]), 'sk_0'), clause(6), {'X': graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))]), 'W': 'sk_0'}, [quoted(graph([triple(iri('https://example.org/s'), iri('https://example.org/p'), literal('hello', lang('en')))]))])
