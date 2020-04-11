import 'package:autocomplete_textfield/autocomplete_textfield.dart';
import 'package:cfapi/services/person.dart';
import 'package:flutter/material.dart';

class FindPenson extends StatefulWidget {
  List<String> suggestions=[];
  FindPenson(this.suggestions);
  
  @override
  _FindPensonState createState() => _FindPensonState(suggestions);
}

class _FindPensonState extends State<FindPenson> {
  String currentText = "";
  List<String> _peoples=[];
  SimpleAutoCompleteTextField textField;
  GlobalKey<AutoCompleteTextFieldState<String>> key = GlobalKey();

  _FindPensonState(List<String> sugs) {
    textField = SimpleAutoCompleteTextField(
      key: key,
      decoration: InputDecoration(hintText: "添加奖扣对象"),
      suggestions: sugs,
      textChanged: (text) => currentText = text,
      clearOnSubmit: true,
      textSubmitted: (text) => setState(() {
        if (text != "" ) {
          _peoples.add(text);
        }
	    }),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      child: Column(
        children: <Widget>[
          ListTile(
            title: textField,
            trailing: Padding(
              padding: const EdgeInsets.only(top:10.0),
              child: IconButton(
                color: Colors.blue,
                iconSize: 30,
                icon: Icon(Icons.group_add),
                onPressed: (){},
              ),
            )
          ),
          Wrap(
            spacing: 8.0, // gap between adjacent chips
            runSpacing: 4.0, 
            children:_peoples.map((String item)=>
              Chip(
                label: Text(item),
                deleteIconColor: Colors.red,
                onDeleted: () {
                  setState(() {
                    _peoples.removeWhere((String name) {
                      return name == item;
                    });
                  });
                },
              )
            ).toList()
          )
        ]
      )
    );
  }
}
  
