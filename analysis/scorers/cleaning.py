def clean(text):
    def replace_whitespace(text):
        return text.replace('\n',' ')
    
    def delete_punctuation(text):
        punctuation = '\,./|<>?;#:@~[]{}`!"£$%^&*()-=_+\''
        for punct in punctuation:
            text = text.replace(punct, ' ')
        return text
    
    no_whitespace = replace_whitespace(text)
    no_punct = delete_punctuation(no_whitespace)
    
    while '  ' in no_punct:
        no_punct = no_punct.replace('  ',' ')

    text_list = [word.lower() for word in no_punct.split(' ') if word!='']

    return text_list

def clean_to_paragraphs(text):
    def replace_whitespace(text):
        return text.split('\n')
    
    def delete_punctuation(text):
        punctuation = '\,./|<>?;#:@~[]{}`!"£$%^&*()-=_+\''
        for punct in punctuation:
            text = text.replace(punct, ' ')
        return text
    
    no_whitespace = replace_whitespace(text)
    no_punct = [delete_punctuation(paragraph) for paragraph in no_whitespace]
    
    for idx,paragraph in enumerate(no_punct):
        while '  ' in paragraph:
            paragraph = paragraph.replace('  ',' ')
            no_punct[idx] = paragraph

    text_list = [[word.lower() for word in paragraph.split(' ') if word!=''] for paragraph in no_punct if paragraph!='']

    return text_list