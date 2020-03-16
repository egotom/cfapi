import 'package:autocomplete_textfield/autocomplete_textfield.dart';
import 'package:flutter/material.dart';

class ScoreProposal extends StatefulWidget {
  ScoreProposal({Key key}) : super(key: key);
  @override
  _ScoreProposalState createState() => _ScoreProposalState();
}

enum ScoreType{ap,an,bp,bn,cp,cn}

class _ScoreProposalState extends State<ScoreProposal> {
  ScoreType _sctp=ScoreType.bp;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(10.0),
      child:Column(
        children: <Widget>[
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: <Widget>[
              AutoCompleteTextField<List>()
            ],
          ),
        ],
      )
    );
  }
}