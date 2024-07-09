import streamlit as st

def write_content(resources_folder):
    # title
    st.title('Karma Coordinates Calculator App')

    # web content
    st.image(f'{resources_folder}/kapil-muni-image.png', caption='Kapil muni 5000 BC')

    pdf = f'<a href="{resources_folder}/samkhya-karika.pdf">pdf</a>'

    txt = '''According to *Sankhya*-yoga by Sage (*Muni*) Kapil (https://en.wikipedia.org/wiki/Samkhyakarika), 
    *Prakriti* (the universe) exists for providing
    experiences to *Purush*. *Purush* upon realization that “I exist” is liberated
    (*Moksha*). Every life-form in *Prakriti* is engaged in providing experiences to a
    *Purush*. Once  all *Purush* are awakened, the *Prakriti*’s work is complete and it
    collapses into a singularity and the next cycle is started with a big-bang. As
    per the open model with omega of 6, universe is 6 billion years old and it
    will end when it is about 13 billion years old - that is in another 7
    billion years (https://en.wikipedia.org/wiki/Ultimate_fate_of_the_universe).    
      A life-form comes into an existence due to a microscopic particle in
    nature called as *Sukshm*. It is Sukshm that gets tinged with the acquired 
    tendencies (*Bhavas*), from life-form to life-form! Once all tendencies are 
    overcome/consumed, *Moksha* is achieved. A human life is the only known form 
    of *Sukshm* that is capable of achieving *Moksha* for its *Purush*. *Sankhya*-yoga 
    quantifies and explains attributes (*Gunas*) and tendencies (*Bhavas*) that can 
    take a life form closer to achieving *Moksha*.  
    Karma Coordinates is a fun app developed to approximate based on your *Gunas* and 
    *Bhavas* your current position in this karmic journey of many lives until *Moksha*. 
    A score of 11/13 means you are at about 11 billion year mark - very near 
    to achieving the awakening state.  A score of 7/13 means you are at 7 billion 
    year mark, ahead but can speed it up by certain lifestyle based changes.      
    Karma Coordinates outcome is also explained in terms of three *Gunas* - *Satva*, 
    *Rajas* and *Tamas*:  
    - *Satva* is the light (*Prakash*) property in the *Prakriti*. The neural network 
    in our brain - our intellect - has the highest *Satva*. 
    - *Rajas* is the energy property in the *Prakriti*. It moves mass. It activates. 
    Our mind and bodies are enabled by *Rajas*. 
    - *Tamas* is the mass property in the *Prakriti* - The flesh and bones of our body 
    has the highest *Tamas*.  
    '''

    st.markdown(txt)
