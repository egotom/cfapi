import 'package:autocomplete_textfield/autocomplete_textfield.dart';
import 'package:flutter/material.dart';

class FirstPage extends StatefulWidget {
  @override
  _FirstPageState createState() => _FirstPageState();
}

class _FirstPageState extends State<FirstPage> {
  List<String> added = [];
  String currentText = "";
  GlobalKey<AutoCompleteTextFieldState<String>> key = GlobalKey();

  _FirstPageState() {
    textField = SimpleAutoCompleteTextField(
      key: key,
      decoration: InputDecoration(errorText: "Beans"),
      controller: TextEditingController(text: "Starting Text"),
      suggestions: suggestions,
      textChanged: (text) => currentText = text,
      clearOnSubmit: true,
      textSubmitted: (text) => setState(() {
		    if (text != "") added.add(text);
	    }),
    );
  }

  List<String> suggestions = ["Apple","Armidillo","Actual","Actuary","America"];
  SimpleAutoCompleteTextField textField;
  bool showWhichErrorText = false;

  @override
  Widget build(BuildContext context) {
    Column body = Column(children: [
      ListTile(
          title: textField,
          trailing: IconButton(
              icon: Icon(Icons.add),
              onPressed: () {
                textField.triggerSubmitted();
                //showWhichErrorText = !showWhichErrorText;
                //textField.updateDecoration(
                //    decoration: InputDecoration(
                //        errorText: showWhichErrorText ? "Beans" : "Tomatoes"));
              })),]);

    body.children.addAll(added.map((item) {
      return ListTile(title: Text(item));
    }));

    return Scaffold(
      resizeToAvoidBottomPadding: false,
      body: body
    );
  }
}