import 'package:cfapi/config/theme.dart';
import 'package:flutter/material.dart';

class MyRank extends StatefulWidget {
  @override
  _MyRankState createState() => _MyRankState();
}

class _MyRankState extends State<MyRank> {
  @override
  Widget build(BuildContext context) {
    return Container(
      child: Row(
        children: <Widget>[
          Expanded(
            child: Card(
              color:MyTheme().scdc,
              child: InkWell(
                splashColor: Colors.white.withAlpha(80),
                child: Container(                      
                  width: 100,
                  height: 100,
                  padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: <Widget>[
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Text('A : ' ,style:MyTheme().scdf),
                          Text('A+: ' ,style:MyTheme().scdf),
                          Text('A-: ' ,style:MyTheme().scdf),
                        ],
                      ),
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Text('--' ,style:MyTheme().scdf),
                          Text('--' ,style:MyTheme().scdf),
                          Text('--' ,style:MyTheme().scdf),
                        ],
                      ),
                    ],
                  ),
                ),
              )
            ),
          ),
          Expanded(
            child: Card(
              color:MyTheme().scdc,
              child: InkWell(
                splashColor: Colors.white.withAlpha(80),
                child: Container(
                  width: 100,
                  height: 100,
                  padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: <Widget>[
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Text('B :' ,style:MyTheme().scdf),
                          Text('B+:' ,style:MyTheme().scdf),
                          Text('B-:' ,style:MyTheme().scdf),
                        ],
                      ),
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Text('--' ,style:MyTheme().scdf),
                          Text('--' ,style:MyTheme().scdf),
                          Text('--' ,style:MyTheme().scdf),
                        ],
                      ),
                    ],
                  ),
                ),
              )
            ),
          ),
          Expanded(
            child: Card(
              color:MyTheme().scdc,
              child: InkWell(
                splashColor: Colors.white.withAlpha(80),
                child: Container(
                  width: 100,
                  height: 100,
                  padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: <Widget>[
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Text('C :' ,style:MyTheme().scdf),
                          Text('C+:' ,style:MyTheme().scdf),
                          Text('C-:' ,style:MyTheme().scdf),
                        ],
                      ),
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Text('--' ,style:MyTheme().scdf),
                          Text('--' ,style:MyTheme().scdf),
                          Text('--' ,style:MyTheme().scdf),
                        ],
                      ),
                    ],
                  ),
                ),
              )
            ),
          ),
        ],
      ),
    );
  }
}