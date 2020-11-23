from ly import document
from ly import music
from ly import lex
from ly.music import read
from ly.music import items

doc = document.Document('''
\paper{
    oddHeaderMarkup=##f
}
''')

def replace_item(doc:items.Document, item:items.Item, new_item:str) -> items.Document:
    with doc.document as d:
        d[item.position:item.end_position()] = new_item
    return music.document(doc.document)

doc = music.document(doc)
paper = list(doc.find_children(items.Paper))[-1]
# for i in paper.find_children(items.Assignment):
#     if i.name() == 'oddHeaderMarkup':
#         scheme_item = i.value().find_child(items.SchemeItem)
#         doc = replace_item(doc, scheme_item, '#tttt')

print(doc.document.plaintext())
print(paper.position, paper.end_position())
 #paper_var = reader.factory(items.Assignment, lex.lilypond.PaperVariable('oddFooterMarkup', -1))
 #scheme_start = reader.factory(items.Scheme, lex.lilypond.SchemeStart('#', -1))
 #scheme_item = reader.factory(items.SchemeItem, lex.scheme.Bool('#f', -1))
 #scheme_start.append(scheme_item)
 #paper_var.append(scheme_start)
 #paper.append(paper_var)
 #
 #print(paper.tokens[0])
 #print(paper_var.token)
 #print(scheme_start.token)
 #print(paper.tokens[1])
