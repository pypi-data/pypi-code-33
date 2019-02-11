query = dict()
parameters = dict()

query['clean'] = '''
query Clean($input: String,$parameters:String) { 
    clean(text:$input,parameters:$parameters) {
        analytics
        querytime
        message
        timestamp    
    }
}    
'''

parameters['clean'] = '''
{
    "cleanType":"minimal"
}
'''

query['metrics'] = '''
query Metrics($input: String,$parameters:String) { 
    metrics(text:$input,parameters:$parameters) {
        analytics {
            words
            sentences
            sentWordCounts
            averageSentWordCount 
        }
        querytime
        message
        timestamp    
    }
}    
'''

parameters['metrics'] = '''
{}
'''


query['annotations'] = '''
query Annotations($input: String,$parameters:String) {
    annotations(text:$input,parameters:$parameters) {
        analytics {
          idx
          start
          end
          length
          tokens {
            idx
            term
            lemma
            postag
            parent
            children
            deptype
            nertag
          }
        }
        querytime
        message
        timestamp
    }
}
'''

parameters['annotations'] = '''
{
    "pipeType":"clu"
}
'''

query['expressions'] = '''
query Expressions($input: String,$parameters:String) {
  expressions(text:$input,parameters:$parameters) {
    analytics {
      sentIdx
      affect{
        text
      }
      epistemic {
        text
        startIdx
        endIdx
      }
      modal {
        text
      }
    }
  }
}
'''

parameters['expressions'] = '''
{}
'''

query['affectExpressions'] = '''
query AffectExpressions($input: String,$parameters:String) { 
    affectExpressions(text:$input,parameters:$parameters) { 
        querytime
        message
        timestamp
        analytics {
            affect {
                text
                valence
                arousal
                dominance
                startIdx
            }
        }
    }}
'''

parameters['affectExpressions'] = '''
{
    "valence":0,
    "arousal":4,
    "dominance":0
}
'''

query['reflectExpressions'] = '''
query ReflectExpressions($input: String,$parameters:String) {
  reflectExpressions(text:$input,parameters:$parameters) {
    querytime
    analytics {
      counts {
        wordCount
        avgWordLength
        sentenceCount
        avgSentenceLength
      }
      summary {
        metaTagSummary {
          knowledge
          experience
          regulation
          none
        }
        phraseTagSummary {
          outcome
          temporal
          pertains
          consider
          anticipate
          definite
          possible
          selfReflexive
          emotive
          selfPossessive
          compare
          manner
          none
        }
      }
      tags {
        sentence
        phrases
        subTags
        metaTags
      }
    }
  }
}
'''

parameters['reflectExpressions'] = '''
{}
'''

query['vocabulary'] = '''
query Vocab($input: String,$parameters:String) {
  vocabulary(text:$input,parameters:$parameters){
    analytics {
      unique
      terms {
        term
        count
      }
    }
    timestamp
  }
}
'''

parameters['vocabulary'] = '''
{}
'''

query['posStats'] = '''
query PosStats($input: String,$parameters:String){
  posStats(text:$input,parameters:$parameters) {
    analytics {
      verbNounRatio
      futurePastRatio
      adjectiveWordRatio
      namedEntityWordRatio
      nounDistribution
      verbDistribution
      adjectiveDistribution
    }
  }
}
'''

parameters['posStats'] = '''
{}
'''

query['syllables'] = '''
query Syllables($input: String,$parameters:String) {
  syllables(text:$input,parameters:$parameters) {
    analytics {
      sentIdx
      avgSyllables
      counts
    }
    timestamp
  }
}
'''

parameters['syllables'] = '''
{}
'''

query['spelling'] = '''
query Spelling($input: String,$parameters:String) {
  spelling(text:$input,parameters:$parameters) {
    timestamp
    message
    querytime
    analytics {
      sentIdx
      spelling {
        message
        suggestions
        start
        end
      }
    }
  }
}
'''

parameters['spelling'] = '''
{}
'''

query['moves'] = '''
query Moves($input: String,$parameters:String) { 
    moves(text:$input,parameters:$parameters) { 
        querytime
        message
        timestamp
        analytics
    }
} 
'''

parameters['moves'] = '''
{
    "grammar":"reflective"
}
'''


query['batch'] = '''
query Batch($parameters:String) { 
    batch(parameters:$parameters) { 
        querytime
        message
        timestamp
        analytics
    }
} 
'''

parameters['batch'] = '''
{
    "analysisType": "reflectExpressions",
    "s3bucket": "",
    "progressCheck": ""
}
'''


query['schema'] = '''
    { __schema { queryType { name ...subtypes } } }
    fragment subtypes on __Type { fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
          name
        }}}}}}}}}}}}}}
'''