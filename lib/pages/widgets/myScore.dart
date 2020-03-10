import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/score.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:date_range_picker/date_range_picker.dart' as DateRagePicker;

class MyScore extends StatefulWidget {
  @override
  _MyScoreState createState() => _MyScoreState();
}

class _MyScoreState extends State<MyScore> {
  ScoreModel scm = ScoreModel();
  String tpClass;
  int tpIdex=0;
  void scFilter(opt) async {
    switch(opt){
      case 'd':
        final List<DateTime> picked = await DateRagePicker.showDatePicker(
            context: context,
            initialFirstDate: DateTime.now(),
            initialLastDate: DateTime.now(),
            firstDate: DateTime(2018),
            lastDate: DateTime(2050)
        );
        if (picked != null && picked.length == 2) {
            print(picked);
        }
        break;
      default:
        int id=tpIdex==2?0:tpIdex+1;
        int idx=opt==tpClass?id:0;
        setState( () {tpClass=opt;tpIdex=idx;} );
        print(opt);
        print(idx);
    }    
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(8.0),
      child: CustomScrollView(
        slivers: <Widget>[
          SliverPersistentHeader(
            floating: true,
            delegate: CustomSliverDelegate(
              expandedHeight: 200.0,
              child: ScoreFilter(scFilter),
            ),
          ),
          SliverFixedExtentList(
            itemExtent: 50.0,
            delegate: SliverChildBuilderDelegate(
              (BuildContext context, int index) {
                return Container(
                  alignment: Alignment.center,
                  color: Colors.lightBlue[100 * (index % 9)],
                  child: Text('list item $index'),
                );
              },
            ),
          )
        ],
      ),
    );
  }
}

class CustomSliverDelegate extends SliverPersistentHeaderDelegate {
  final double expandedHeight;
  final Widget child;

  CustomSliverDelegate({
    @required this.expandedHeight,
    @required this.child,
  });

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return child;
  }

  @override
  double get maxExtent => expandedHeight;

  @override
  double get minExtent => expandedHeight;

  @override
  bool shouldRebuild(SliverPersistentHeaderDelegate oldDelegate) {
    return true;
  }
}

class ScoreFilter extends StatefulWidget {
  final _fn;
  const ScoreFilter(this._fn,{Key key}) : super(key: key);
  @override
  _ScoreFilterState createState() => _ScoreFilterState();
}

class _ScoreFilterState extends State<ScoreFilter> {

  @override
  Widget build(BuildContext context) {
    return Column(      
      children:<Widget>[
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: <Widget>[
            FlatButton(
              child: Text('2019.3-2020.10', style:TextStyle(color:Colors.blue[400])),
              onPressed: ()=>widget._fn('d'),
            ),
            IconButton(
              icon: Icon(Icons.date_range, color:Colors.blue[400]), 
              onPressed: ()=>widget._fn('d') 
            ),
          ],
        ),
        Row(
          children: <Widget>[
            Expanded(
              child: Card(
                color:Colors.blue,
                child: InkWell(
                  splashColor: Colors.white.withAlpha(80),
                  onTap: ()=>widget._fn('a'),
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Container(
                      width: 120,
                      height: 120,
                      child: Text('A card that can be tapped'),
                    ),
                  ),
                )
              ),
            ),
            Expanded(
              child: Card(
                color:Colors.blue,
                child: InkWell(
                  splashColor: Colors.white.withAlpha(80),
                  onTap: ()=>widget._fn('b'),
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Container(
                      width: 120,
                      height: 120,
                      child: Text('A card that can be tapped'),
                    ),
                  ),
                )
              ),
            ),
            Expanded(
              child: Card(
                color:Colors.blue,
                child: InkWell(
                  splashColor: Colors.white.withAlpha(80),
                  onTap: ()=>widget._fn('c'),
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Container(
                      width: 120,
                      height: 120,
                      child: Text('A card that can be tapped'),
                    ),
                  ),
                )
              ),
            ),
          ],
        )
      ] 
    );
  }
}
