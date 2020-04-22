
import 'package:flutter/material.dart';
class LotteryCard extends StatelessWidget {
  final String img;
  final String txt1;
  final String txt2;
  final String txt3;
  const LotteryCard({Key key, this.img, this.txt1, this.txt2, this.txt3}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(10),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children:<Widget>[
          Image(
            width: MediaQuery.of(context).size.width*0.6,
            image: AssetImage(img),
            fit: BoxFit.cover,            
          ),
          Container(
            padding: EdgeInsets.only(bottom: 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children:<Widget>[
                Text(txt1,style: TextStyle(fontSize:16,height: 2.5)),
                Text(txt2,style: TextStyle(fontSize:16,height: 2.5)),
                Text(txt3,style: TextStyle(fontSize:16,height: 2.5))
              ]
            ),
          )
        ]
      ),
    );
  }
}