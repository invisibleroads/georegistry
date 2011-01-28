'Routines for formatting email'
# Import system modules
import string
import re


pattern_address = re.compile(r'<.*?>')
pattern_bracket = re.compile(r'<|>')
pattern_domain = re.compile(r'@[^,]+|/[^,]+')


def formatHeader(subject, when, fromWhom, toWhom, ccWhom, bccWhom):
    # Unicode everything
    subject = unicodeSafely(subject)
    fromWhom = unicodeSafely(fromWhom)
    toWhom = unicodeSafely(toWhom)
    ccWhom = unicodeSafely(ccWhom)
    bccWhom = unicodeSafely(bccWhom)
    # Build header
    header = 'From:       %(fromWhom)s\nDate:       %(date)s\nSubject:    %(subject)s' % {
        'fromWhom': fromWhom,
        'date': when.strftime('%A, %B %d, %Y    %I:%M:%S %p'),
        'subject': subject,
    }
    # Add optional features
    if toWhom:
        header += '\nTo:         %s' % toWhom
    if ccWhom:
        header += '\nCC:         %s' % ccWhom
    if bccWhom:
        header += '\nBCC:        %s' % bccWhom
    # Return
    return header

def formatToWhomString(toWhom, ccWhom, bccWhom):
    return ', '.join(filter(lambda x: x, (y.strip() for y in (toWhom, ccWhom, bccWhom))))

def formatNameString(nameString):
    # Split the string
    oldTerms = nameString.split(',')
    newTerms = []
    # For each term,
    for oldTerm in oldTerms:
        # Try removing the address
        newTerm = pattern_address.sub('', oldTerm).strip()
        # If the term is empty,
        if not newTerm:
            # Remove brackets
            newTerm = pattern_bracket.sub('', oldTerm).strip()
        # Append
        newTerms.append(newTerm)
    # Remove domain
    string = pattern_domain.sub('', ', '.join(newTerms))
    # Return
    return string.replace('"', '').replace('.', ' ')

def unicodeSafely(s):
    if isinstance(s, unicode):
        return s.encode('ascii', 'ignore')
    return unicode(s, 'ascii', errors='ignore')

def sanitizeFileName(fileName):
    alphabet = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(x if x in alphabet else '-' for x in fileName)

def prepareTagText(text):
    # Return lowercase, remove quotation marks and whitespace
    return text.lower().strip('" ')
