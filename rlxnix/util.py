def nix_metadata_to_dict(section):
    info = {}
    for p in section.props:
        info[p.name] = ([v for v in p.values], p.unit)
    for s in section.sections:
        info[s.name] = nix_metadata_to_dict(s)
    return info
