import 'package:flutter/material.dart';

Widget Span(String k,String v){
  return RichText(
    text: TextSpan(
      text: k,
      style: TextStyle(color:Colors.blue,height: 2),
      children: <TextSpan>[
        TextSpan(text:v, style: TextStyle(color:Colors.black))
      ]
    )
  );
}