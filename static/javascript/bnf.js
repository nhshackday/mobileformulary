
var drugs = _.map(_.keys(bnf),
                function(drug){
                    return drug.toLowerCase()
                })

function search(text){
    return _.filter(drugs, function(name){
        if (name.indexOf(text.toLowerCase()) == 0){
            return name
        }else{
            return false
        }
    });
}