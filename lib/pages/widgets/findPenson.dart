import 'package:autocomplete_textfield/autocomplete_textfield.dart';
import 'package:flutter/material.dart';

class FindPenson extends StatefulWidget {
  @override
  _FindPensonState createState() => _FindPensonState();
}

class _FindPensonState extends State<FindPenson> {
  List<String> added = [];
  String currentText = "";
  GlobalKey<AutoCompleteTextFieldState<String>> key = GlobalKey();

  _FindPensonState() {
    textField = SimpleAutoCompleteTextField(
      key: key,
      decoration: InputDecoration(
        hintText: "添加奖扣对象"
      ),
      //controller: TextEditingController(text: "Starting Text"),
      suggestions: suggestions,
      textChanged: (text) => currentText = text,
      clearOnSubmit: true,
      textSubmitted: (text) => setState(() {
        if (text != "") {
          added.add(text);
        }
	    }),
    );
  }

  List<String> suggestions = ["Australia","Antarctica","Blueberry","Hazelnut","Ice Cream","Jely","Kiwi Fruit","Lamb","Macadamia","Nachos","Oatmeal","Palm Oil","Quail","Rabbit","Salad","T-Bone Steak","Urid Dal","Vanilla",];
  SimpleAutoCompleteTextField textField;

  @override
  Widget build(BuildContext context) {
    Column body = Column(
      children: <Widget>[
        ListTile(
          title: textField,
          trailing: Padding(
            padding: const EdgeInsets.only(top:10.0),
            child: IconButton(
                color: Colors.blue,
                iconSize: 30,
                icon: Icon(Icons.group_add),
                onPressed: () {
                  textField.triggerSubmitted();
                  textField.updateDecoration();
                }),
          ))
    ]);

    body.children.addAll(added.map((item) {
      return ListTile(title: Text(item));
    }));

    return Container(
      child: body
    );
  }
}