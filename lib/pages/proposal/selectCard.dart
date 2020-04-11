import 'package:cfapi/services/rule.dart';
import 'package:flutter/material.dart';

class SelectCard extends StatefulWidget {
  final Rule _rule;
  final Function _onSelect;  
  SelectCard(this._rule,this._onSelect);

  @override
  _SelectCardState createState() => _SelectCardState();
}

class _SelectCardState extends State<SelectCard> {
  Color selected;
  @override
  Widget build(BuildContext context) {
    return Container(
      width: MediaQuery.of(context).size.width,
      padding: const EdgeInsets.fromLTRB(0, 10, 0, 10),
      child: Card(
        margin:EdgeInsets.symmetric(),
        color: Colors.amber,
        child: InkWell(
          onTap: (){
            widget._onSelect();
            
          },
          splashColor: Colors.white.withAlpha(80),
          child: Padding(
            padding: const EdgeInsets.all(10.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.start,
              children:<Widget>[
                Text(widget._rule.serial),
                Text('${widget._rule.classify}${widget._rule.score}'),
                Text(widget._rule.description),
              ]
            ),
          ),
        ),
      ),
    );
  }
}