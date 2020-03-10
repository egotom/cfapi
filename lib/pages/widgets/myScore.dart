import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:date_range_picker/date_range_picker.dart' as DateRagePicker;

class Score extends StatefulWidget {
  @override
  _ScoreState createState() => _ScoreState();
}

class _ScoreState extends State<Score> {

  dateSel() async{
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
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          children: <Widget>[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                FlatButton(
                  child: Text('2019.3-2020.10', style:TextStyle(color:Colors.blue[400])),
                  onPressed: dateSel,
                ),
                IconButton(
                  icon: Icon(Icons.date_range, color:Colors.blue[400]), 
                  onPressed: dateSel 
                ),
              ],
            ),
            
            Row(
              children: <Widget>[
                Expanded(
                  child: Card(
                    color:Colors.redAccent,
                    child: InkWell(
                      splashColor: Colors.blue.withAlpha(30),
                      onTap: (){},
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
                    color:Colors.redAccent,
                    child: InkWell(
                      splashColor: Colors.blue.withAlpha(30),
                      onTap: (){},
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
                    color:Colors.redAccent,
                    child: InkWell(
                      splashColor: Colors.blue.withAlpha(30),
                      onTap: (){},
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
          ],
        ),
      ),
    );
  }
}