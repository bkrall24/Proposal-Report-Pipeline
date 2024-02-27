import spacy
# import pyinflect
import lemminflect
import re


def find_subject_plural(token):

    # subjs = [t for t in token.ancestors if 'subj' in t.dep_]
    subjs = [t for t in token.lefts if 'subj' in t.dep_]
    # nouns = [t for t in token.lefts if 'NOUN' in t.dep_]
    nouns = [t for t in token.sent[:token.i] if 'NOUN' in t.pos_]


    if subjs:
        morph = subjs[0].morph.to_dict()
        if 'Number' in morph.keys():
            return morph['Number']
        elif 'S' in subjs[0].tag_:
            return 'Plur'
        else:
            return 'Sing'
            
            
    elif nouns:
        morph = nouns[-1].morph.to_dict()
        if 'Number' in morph.keys():
            return morph['Number']
        elif 'S' in nouns[-1].tag_:
            return 'Plur'
        else:
            return 'Sing'
    
    else:
        return 'Sing'
    


def past_tensify(txt):

    nlp = spacy.load('en_core_web_sm')
    doc = nlp(txt)
    out = list()
    words = []
    aux_count = 0
    aux_phrase = []

    if len(doc) > 2:

        for word in doc:
            words.append(word)
            new_word = None
            tag = word.tag_
            pos = word.pos_
            dep = word.dep_

            # Do not append word if is a auxillary word that is not the Root and not preceeded by 'to'
            # Keep track of auxillary words
            if 'AUX' in pos and dep != 'ROOT' and out[-1].text.lower() != 'to': # and word.text != 'is':
                aux_count = aux_count +1
                aux_phrase.append(word.lemma_)
            
            # Append other words, but look for specific patterns to change tenses
            else:  

                # Identify verbs that should be altered
                if (dep == "ROOT") or ('cl' in dep) or ('conj' in dep) :
                    
                    # Determine if the subject of this word is plural or singular
                    plural = find_subject_plural(word)

                    # Determine all adverbs tied to the verb
                    adverbs = [a for a in word.children if 'RB' in a.tag_]

                    # Identify 'be' in auxillary clause (will be, have been) to replace with was/were
                    # Identify 'be' in conjuction with past participle (are having, am walking) to replace with was/were
                    if ((('be' in aux_phrase) or ('am' in aux_phrase) ) and aux_count > 1) or \
                        ((('be' in aux_phrase) or ('am' in aux_phrase) ) and word.tag_ in ['VBN', 'VBG']): 

                        if word.tag_ != 'VBG':
                            if plural == 'Sing':
                                out.append(nlp('was')[0])
                            else:
                                out.append(nlp('were')[0])
                        else:
                            new_word = word._.inflect('VBD', form_num = 0)
                    
                        aux_count = 0
                        aux_phrase = []

                    # If verb is in specific form and not proceeded by 'to', change the tense. Note, I exclude 'see' here because proposals sometimes say
                    # "see table 1" or similar. 
                    if (tag in ['VB', 'VBP']) and ( word.text.lower() != 'see') and out[-1].text.lower() != 'to': # removed VBN and VBZ as a test

                        if word.lemma_ == 'be':
                            if plural == 'Sing':
                                new_word = 'was'
                            else:
                                new_word = 'were'
                        else:      
                            if plural == 'Sing':
                                new_word = word._.inflect('VBD', form_num = 0)
                            else:
                                new_word = word._.inflect('VBD', form_num = 1)

                    # If not the specific type of verb, just append the word 
                    # elif new_word is None:
                    #     new_word = word.text
                    

                    # Keep adverbs in the correct spot relative to the verb
                    for adv in adverbs:
                        if (adv in out[1:]) and (adv.i in range(word.i - (len(adverbs)+1), word.i + (len(adverbs)+1))):
                            out.pop(out.index(adv))
                            out.append(adv)

                    # If we've changed the word, append that. If not, just append the word
                    if new_word is not None:
                        out.append(nlp(new_word)[0])
                    else:
                        out.append(word)
                    
                    aux_count = 0
                    aux_phrase = []
                
                else:
                    out.append(word)
    
    
    # all_words = [t.text for t in out]
        # out = format_word_list(all_words)
        if len(out) > 0:
            result = format_word_list(out)
        else:
            result = out
    
    else:
        result = txt

    return result
    
  

def tense_correct_para(txt):
    delimiters = r'[.:;\t]'
    chunks = re.split(delimiters, txt)
    for c in chunks:
        new_chunk = past_tensify(c)
        if len(new_chunk) > 0 and (c != new_chunk):
            txt = txt.replace(c, new_chunk)

    return txt





def format_word_list(doc):
    # add a space after unless the next word is a in [.,?!):;]}
    no_space_before = ['.',',',')','}',']',';',':','!', '?' , '-', '/', "°"]
    no_space_after = ['(', '[', '{', '-', '/', "°"]
    out = []
    out.append(doc[0].text)
    exclude_next_space = False

    for t in doc[1:]:

        if (not t.text in no_space_before) and not ( "’" in t.text) and not ("'" in t.text) and not (exclude_next_space):
            out.append(" "+ t.text)
        else:
            out.append(t.text)
        
        if t.text in no_space_after:
            exclude_next_space = True
        else:
            exclude_next_space = False

        
    return "".join(out)