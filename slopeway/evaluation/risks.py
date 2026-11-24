from .chronology import contains


def active_closures(notices, when):
    return [
        {key: row[key] for key in ('ref', 'start', 'end', 'reason')}
        for row in notices if contains(row['start'], row['end'], when)
    ]
