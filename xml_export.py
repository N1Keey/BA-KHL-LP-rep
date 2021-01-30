import xml.etree.ElementTree as ET
from datetime import datetime

#build tree

def create_quiz(headerelements, fragendicts):
    quiz=ET.Element('quiz')
    for textelement in headerelements:
        quiz.append(create_question_header(textelement))
    for fragendict in fragendicts:
        quiz.append(create_question_main(fragendict))
    return quiz

def create_question_header(headerelement):
    question=ET.Element('question', type='category')
    question.append(create_category_header(headerelement))
    return question

def create_category_header(headerelement):
    category=ET.Element('category')
    category.append(create_text_header(headerelement))
    return category

def create_text_header(headerelement):
    text = ET.Element('text')
    text.text=headerelement
    return text

def create_question_main(fragendict):
    question=ET.Element('question', type='multichoice')
    fragentitel=fragendict.get('Fragentitel')
    question.append(create_name_main_kh(fragentitel))
    #fragen
    questiontext=ET.Element('questiontext', format='html')
    text=ET.Element('text')
    text.text=fragendict.get('Frage')
    questiontext.append(text)
    question.append(questiontext)
    #settings
    defaultgrade=ET.Element('defaultgrade')
    defaultgrade.text='%s'%(len(fragendict.get('Antworten')))
    question.append(defaultgrade)
    singleans=ET.Element('single')
    singleans.text='false'
    question.append(singleans)
    shuffleanswers=ET.Element('shuffleanswers')
    shuffleanswers.text='true'
    question.append(shuffleanswers)
    answernumbering=ET.Element('answernumbering')
    answernumbering.text='none'
    question.append(answernumbering)
    #feedback
    (correctfeedback,partiallycorrectfeedback,incorrectfeedback)=create_feedback_main()
    question.append(correctfeedback)
    question.append(partiallycorrectfeedback)
    question.append(incorrectfeedback)
    #antworten           
    question=create_answer_main(question, fragendict)
    return question

def create_name_main_kh(fragentitel):
    name=ET.Element('name')
    name.append(create_text_main_kh(fragentitel))
    return name

def create_text_main_kh(fragentitel):
    text=ET.Element('text')
    text.text=fragentitel
    return text

def create_feedback_main():
    correctfeedback=ET.Element('correctfeedback', format='html')
    text=ET.Element('text')
    text.text='Die Antwort ist richtig'
    correctfeedback.append(text)
    
    partiallycorrectfeedback=ET.Element('partiallycorrrectfeedback', format='html')
    text=ET.Element('text')
    text.text='Die Antwort ist teilweise richtig'
    partiallycorrectfeedback.append(text)
    
    incorrectfeedback=ET.Element('incorrectfeedback', format='html')
    text=ET.Element('text')
    text.text='Die Antwort ist falsch'
    incorrectfeedback.append(text)
    return correctfeedback, partiallycorrectfeedback, incorrectfeedback

def create_answer_main(question, fragendict):
    rcounter=0
    for antwort in fragendict.get('Antworten'):
        if fragendict.get('Antworten').get(antwort)=='right':
            rcounter+=1
    if rcounter == 0:
        pointsright=0
    else:
        pointsright=100/rcounter
    pointswrong=100/((len(fragendict.get('Antworten'))-rcounter))
    for antwort in fragendict.get('Antworten'):
        if fragendict.get('Antworten').get(antwort)=='right':
            answer=ET.Element('answer', format='html', fraction='%s'%pointsright)
        else:
            answer=ET.Element('answer', format='html', fraction='-%s'%pointswrong)
        text=ET.Element('text')
        text.text=('%s'%(antwort))
        answer.append(text)
        question.append(answer)
    return question

def create_file(fragendicts):
    #header
    dt=datetime.now()
    dtstring=dt.strftime('%Y.%m.%d_%H:%M')
    coursetop='$course$/Krankheitslehrefragen(%s)'%dtstring
    ba_mit_fragen=coursetop
    headerelements=[coursetop, ba_mit_fragen]
    #main
    quiz=create_quiz(headerelements, fragendicts)
    data=ET.tostring(quiz)
    exportfile=open('Quizexport.xml', 'wb')
    exportfile.write(data)
    exportfile.close()


#export to File