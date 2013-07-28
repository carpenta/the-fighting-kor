var defaultSettings = {
  screenWidth: 1000,
  screenHeight: 800,
  strokeSize: 5,
  strokeColor: 'gray',
  depth: 2,
  boxPadding: 20,
  boxWidth: 100,
  boxHeight: 50,
  zonePadding: 20,
  zoneWidth: 150,
  zoneHeight: 100,
  zoneMargin: 200
};

function generateUUID(){
  var d = new Date().getTime();
  var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = (d + Math.random()*16)%16 | 0;
    d = Math.floor(d/16);
    return (c=='x' ? r : (r&0x7|0x8)).toString(16);
  });
  return uuid;
};

function makeDropZone(boxInfo, data){
  var result = new Kinetic.Group({
    x: boxInfo.x,
    y: boxInfo.y,
    width: boxInfo.width,
    height: boxInfo.height
  });
  result.id = data.id;
  result.info = boxInfo;
  result.occupied = false;

  var title = new Kinetic.Text({
    text: data.text,
    fontSize: 18,
    fontFamily: 'Calibri',
    fill: '#555',
    width: boxInfo.width,
    height: boxInfo.height,
    padding: 20,
    align: 'center',
    verticalAlign: 'middle'
  });

  var rect = new Kinetic.Rect({
    stroke: '#555',
    strokeWidth: 5,
    fill: '#ddd',
    width: boxInfo.width,
    height: boxInfo.height,
    shadowColor: 'black',
    shadowBlur: 10,
    shadowOffset: [10, 10],
    shadowOpacity: 0.2,
    cornerRadius: 10
  });

  result.add(rect);
  result.add(title);

  return result;
}

function checkIntersection(zones, boxPosition) {
  var zone = null;
  for (var a in zones) {
    var zonePos = zones[a].getPosition();
    var zoneSize = zones[a].getSize();
    if(zonePos.x < boxPosition.x 
      && zonePos.y < boxPosition.y
      && zonePos.x + zoneSize.width > boxPosition.x 
      && zonePos.y + zoneSize.height > boxPosition.y) {
      zone = zones[a];
      break;
    }
  }
  return zone;
}

function makeBox(boxInfo, data, dropCallback){
  var result = new Kinetic.Group({
    draggable: true,
    x: boxInfo.x,
    y: boxInfo.y,
    width: boxInfo.width,
    height: boxInfo.height
    /*
    dragBoundFunc: function(pos) {
      return {
        x: pos.x,
        y: this.getAbsolutePosition().y
      }
    }
    */
  });

  result.id = data.id;
  result.info = boxInfo;
  result.occupyZone = null;

  var complexText = new Kinetic.Text({
    text: data.text,
    fontSize: 18,
    fontFamily: 'Calibri',
    fill: '#555',
    width: boxInfo.width,
    padding: 20,
    align: 'center'
  });

  var rect = new Kinetic.Rect({
    stroke: '#555',
    strokeWidth: 5,
    fill: '#fff',
    width: boxInfo.width,
    height: complexText.getHeight(),
    shadowColor: 'black',
    shadowBlur: 10,
    shadowOffset: [10, 10],
    shadowOpacity: 0.2,
    cornerRadius: 10
  });

  result.add(rect);
  result.add(complexText);

  result.on('dragend', dropCallback);

  return result;
}