evalscript_slc = """
    function setup() {
      return {
        input: ["SCL"], // You need to add here all the bands you are going to use
        output: {
            bands: 1,
            sapmleType: "FLOAT32"
        }
      };
    }
"""

evalscript_all_bands_l1c = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B10","B11","B12"],
                units: "DN"
            }],
            output: {
                bands: 13,
                sampleType: "INT16"
            }
        };
    }
    function updateOutputMetadata(scenes, inputMetadata, outputMetadata) {
      outputMetadata.userData = { "metadata":  JSON.stringify(scenes) }
    }
    function evaluatePixel(sample) {
        return [sample.B01,
                sample.B02,
                sample.B03,
                sample.B04,
                sample.B05,
                sample.B06,
                sample.B07,
                sample.B08,
                sample.B8A,
                sample.B09,
                sample.B10,
                sample.B11,
                sample.B12];
    }
"""

evalscript_all_bands = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12", "AOT", "SCL", "CLD", "CLP", "CLM"],
                units: "DN"
            }],
            output: {
                bands: 17,
                sampleType: "INT16"
            }
        };
    }
    function updateOutputMetadata(scenes, inputMetadata, outputMetadata) {
      outputMetadata.userData = { "metadata":  JSON.stringify(scenes) }
    }
    function evaluatePixel(sample) {
        return [sample.B01,
                sample.B02,
                sample.B03,
                sample.B04,
                sample.B05,
                sample.B06,
                sample.B07,
                sample.B08,
                sample.B8A,
                sample.B09,
                sample.B11,
                sample.B12,
                sample.AOT,
                sample.SCL,
                sample.CLD,
                sample.CLP,
                sample.CLM];
    }
"""

evalscript_true_color = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04"]
            }],
            output: {
                bands: 3
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B04*2, sample.B03*2, sample.B02*2];
    }
"""

evalscript_NDCI = """
// CyanoLakes Chlorophyll-a L1C
// Jeremy Kravitz & Mark Matthews (2020)

// Water body detection - credit Mohor Gartner
var MNDWI_threshold=0.42; //testing shows recommended 0.42 for Sentinel-2 and Landsat 8. For the scene in article [1] it was 0.8.
var NDWI_threshold=0.4; //testing shows recommended 0.4 for Sentinel-2 and Landsat 8. For the scene in article [1] it was 0.5.
var filter_UABS=true;
var filter_SSI=false;
function wbi(r,g,b,nir,swir1,swir2) {
    //water surface
    let ws=0;
    //try as it might fail for some pixel
    try {
        //calc indices
        //[4][5][1][8][2][3]
        var ndvi=(nir-r)/(nir+r),mndwi=(g-swir1)/(g+swir1),ndwi=(g-nir)/(g+nir),ndwi_leaves=(nir-swir1)/(nir+swir1),aweish=b+2.5*g-1.5*(nir+swir1)-0.25*swir2,aweinsh=4*(g-swir1)-(0.25*nir+2.75*swir1);
        //[10][11][12]
        var dbsi=((swir1-g)/(swir1+g))-ndvi,wii=Math.pow(nir,2)/r,wri=(g+r)/(nir+swir1),puwi=5.83*g-6.57*r-30.32*nir+2.25,uwi=(g-1.1*r-5.2*nir+0.4)/Math.abs(g-1.1*r-5.2*nir),usi=0.25*(g/r)-0.57*(nir/g)-0.83*(b/g)+1;
        //DEFINE WB
        if (mndwi>MNDWI_threshold||ndwi>NDWI_threshold||aweinsh>0.1879||aweish>0.1112||ndvi<-0.2||ndwi_leaves>1) {ws=1;}
        //filter urban areas [3] and bare soil [10]
        if (filter_UABS && ws==1) {
            if ((aweinsh<=-0.03)||(dbsi>0)) {ws=0;}
        }
    }catch(err){ws=0;}
    return ws;
}
let water = wbi(B04,B03,B02,B08,B11,B12);

// Floating vegetation
function FAI (a,b,c) {return (b-a-(c-a)*(783-665)/(865-665))};
let FAIv = FAI(B04,B07,B8A);

// Chlorophyll-a
function NDCI (a,b) {return (b-a)/(b+a)};
let NDCIv = NDCI(B04,B05);
let chl = 826.57 * NDCIv**3 - 176.43 * NDCIv**2 + 19 * NDCIv + 4.071; // From simulated data

// Ture colour
let trueColor = [3*B04,3*B03,3*B02];

// Render colour map
if (water==0) {
    return trueColor;
} else if (FAIv>0.08){
    return [233/255,72/255,21/255];
} else if (chl<0.5){
    return [0,0,1.0];
} else if (chl<1){
    return [0,0,1.0];
} else if (chl<2.5){
    return [0,59/255,1];
} else if (chl<3.5){
    return [0,98/255,1];
} else if (chl<5){
    return [15/255,113/255,141/255];
} else if (chl<7){
    return [14/255,141/255,120/255];
} else if (chl<8){
    return [13/255,141/255,103/255];
} else if (chl<10){
    return [30/255,226/255,28/255];
} else if (chl<14){
    return [42/255,226/255,28/255];
} else if (chl<18){
    return [68/255,226/255,28/255];
} else if (chl<20){
    return [68/255,226/255,28/255];
} else if (chl<24){
    return [134/255,247/255,0];
} else if (chl<28){
    return [140/255,247/255,0];
} else if (chl<30){
    return [205/255,237/255,0];
} else if (chl<38){
    return [208/255,240/255,0];
} else if (chl<45){
    return [208/255,240/255,0];
} else if (chl<50){
    return [251/255,210/255,3/255];
} else if (chl<75){
    return [248/255,207/255,2/255];
} else if (chl<90){
    return [134/255,247/255,0];
} else if (chl<100){
    return [245/255,164/255,9/255];
} else if (chl<150){
    return [240/255,159/255,8/255];
} else if (chl<250){
    return [237/255,157/255,7/255];
} else if (chl<300){
    return [239/255,118/255,15/255];
} else if (chl<350){
    return [239/255,101/255,15/255];
} else if (chl<450){
    return [239/255,100/255,14/255];
} else if (chl<500){
    return [233/255,72/255,21/255];
} else return [233/255,72/255,21/255];
"""

# TODO: Hay que citarlo en la memoria
evalscript_MAGO = """
    //VERSION=3
    // User must set these three values
    var indexNumber = 5; // Necessary to choose the visualization option
    var minValue = 0;
    var maxValue = 200;

    // Color Scale
    var scaleLimits = [2, 6, 6.5, 7, 8, 10, 12]; // Turbidez, índice 5
    //var scaleLimits = [10, 14, 14.5, 15, 16, 18, 25]; // Clorofila > 5, índice 1
    //var scaleLimits = [2, 4, 6, 8, 10, 12, 14] // Clorofila, índice 0
    
    //var scaleLimits = [minValue, (maxValue + 3 * minValue) / 4, (maxValue + minValue) / 2, (3 * maxValue + minValue) / 4, maxValue]
    var s = 255; // Values range from 0 to 255 for every color channel
    var colorScale =  // Define the RGB colors for each border
      [
        [0 / s, 0 / s, 0 / s], //Black
        //[255 / s, 0 / s, 255 / s], // Purple
        [0 / s, 0 / s, 255 / s], // Blue
        [0 / s, 255 / s, 255 / s], // Cyan
        [0 / s, 255 / s, 0 / s], // Green
        [255 / s, 255 / s, 0 / s], // Yellow
        [255 / s, 70 / s, 0 / s], // Orange
        [255 / s, 0 / s, 0 / s], // Red
      ];

    // For evalscript V3 you need to specify two functions
    //    setup() - where you specify inputs and outputs
    //    evaluatePixel() - which calculates the output values for each pixel
    function setup() {
      return {
        input: ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "SCL", "dataMask"], // You need to add here all the bands you are going to use
        output: [
          { id: "default", bands: 3 },
          { id: "index", bands: 1, sampleType: "FLOAT32" },
          { id: "eobrowserStats", bands: 2, sampleType: 'FLOAT32' },
          { id: "dataMask", bands: 1 }
        ]
      };
    }

    function evaluatePixel(samples) {
      let NDWI = index(samples.B03, samples.B08); // Calculate the Normalized Difference Water Index, used in visualization
      let TrueColor = [samples.B04 * 2.5, samples.B03 * 2.5, samples.B02 * 2.5]; // Define true color composites multiplying each band by 2.5 to improve the appearance of images, used in visualization

      // Visualization
      // choose which one to use for visualization by setting indexNumber at the beginning of the code
      // indexNumber = 0 | Chlorophyll a mg / m3 (Mishra 2012 – Based on NDCI) 
      let index0 = 14.039 + (86.11 * (samples.B05 - samples.B04) / (samples.B05 + samples.B04)) + (194.325 * Math.pow((samples.B05 - samples.B04) / (samples.B05 + samples.B04), 2));
      let viz0 = colorBlend(index0, scaleLimits, colorScale);
      // indexNumber = 1 | Chlorophyll a for high values > 5 mg / m3 (Soria-Perpinyà 2021)
      let index1 = 19.866 * Math.pow(samples.B05 / samples.B04, 2.3051);
      let viz1 = colorBlend(index1, scaleLimits, colorScale);
      // indexNumber = 2 | Chlorophyll a  low values < 5 mg / m3 (Soria-Perpinyà 2021) 
      let index2 = Math.pow(10, -2.4792 * Math.log10(Math.max(samples.B03, samples.B02) / samples.B03) - 0.0389);
      let viz2 = colorBlend(index2, scaleLimits, colorScale);
      // indexNumber = 3 | Cyanobacteria (phycocyanin) cells/mL (Potes et al. 2018)
      let index3 = 115530.31 * Math.pow((samples.B03 * samples.B04) / samples.B02, 2.38);
      let viz3 = colorBlend(index3, scaleLimits, colorScale);
      // indexNumber = 4 | Cyanobacteria (Phycocyanin) mg/m3 (Soria-Perpinyà 2021)
      let index4 = 21.554 * Math.pow((samples.B05 / samples.B04), 3.47941);
      let viz4 = colorBlend(index4, scaleLimits, colorScale);
      // indexNumber = 5 | Turbidity NTU (Zhan et al. 2022)
      let index5 = 194.79 * (samples.B05 * (samples.B05 / samples.B02)) + 0.9061;
      let viz5 = colorBlend(index5, scaleLimits, colorScale);
      // indexNumber = 6 | CDOM ug/L (Soria-Perpinyà 2021)
      let index6 = 2.4072 * (samples.B04 / samples.B02) + 0.0709;
      let viz6 = colorBlend(index6, scaleLimits, colorScale);
      // indexNumber = 7 | Total Suspended Solids (TSS) mg/L (Soria-Perpinyà 2021)
      let index7 = 14.464 * (samples.B07 / samples.B02) + 16.336;
      let viz7 = colorBlend(index7, scaleLimits, colorScale);
      // indexNumber = 8 | Clorofila, mg/m3
      //let index8 = (124.94*(samples.B3 + samples.B5)/(samples.B3 + samples.B4)) - 115.35
      let index8 = 32.448 * (samples.B5 / samples.B4) - 21.408;
      let viz8 = colorBlend(index8, scaleLimits, colorScale);

      let imgVals = null;
      let val = NaN;
      // We made a first filter by NDWI (Water Index)
      if (NDWI < -0) { // If NDWI is lower than 0 is not water, so return  true color
        imgVals = [...TrueColor, samples.dataMask];
      } else { // Evaluate indexNumber
        switch (indexNumber) {
          case 0: // indexNumber = 0
            imgVals = [...viz0, samples.dataMask];
            val = index0;
            break;
          case 1: // indexNumber = 1
            imgVals = [...viz1, samples.dataMask];
            val = index1;
            break;
          case 2: // indexNumber = 2
            imgVals = [...viz2, samples.dataMask];
            val = index2;
            break;
          case 3: // indexNumber = 3
            imgVals = [...viz3, samples.dataMask];
            val = index3;
            break;
          case 4: // indexNumber = 4
            imgVals = [...viz4, samples.dataMask];
            val = index4;
            break;
          case 5: // indexNumber = 5
            imgVals = [...viz5, samples.dataMask];
            val = index5;
            break;
          case 6: // indexNumber = 6
            imgVals = [...viz6, samples.dataMask];
            val = index6;
            break;
          case 7: // indexNumber = 7
            imgVals = [...viz7, samples.dataMask];
            val = index7;
            break;
          case 8:
            imgVals = [...viz8, samples.dataMask];
            val = index8;
            break;
          default: // By default true color
            imgVals = [...TrueColor, samples.dataMask];
        }
      }

      // The library for tiffs works well only if there is only one channel returned. 
      // So we encode the "no data" as NaN here and ignore NaNs on frontend. 
      const indexVal = samples.dataMask === 1 ? val : NaN;

      return {
        default: imgVals,
        index: [indexVal],
        eobrowserStats: [val, isCloud(samples.SCL) ? 1 : 0],
        dataMask: [samples.dataMask]
      };
    }

    function isCloud(scl) {
      if (scl == 3) {
        // SC_CLOUD_SHADOWS
        return true;
      } else if (scl == 9) {
        // SC_CLOUD_HIGH_PROBABILITY
        return true;
      } else if (scl == 8) {
        // SC_CLOUD_MEDIUM_PROBABILITY
        return true;
      } else if (scl == 7) {
        // SC_UNCLASSIFIED
        return false;
      } else if (scl == 10) {
        // SC_THIN_CIRRUS
        return true;
      } else if (scl == 11) {
        // SC_SNOW_ICE
        return true;
      } else if (scl == 1) {
        // SC_SATURATED_OR_DEFECTIVE
        return true;
      } else if (scl == 2) {
        // SC_DARK_FEATURE_SHADOW
        return false;
      } else {
        return false;
      }
    }
"""

evalscript_ulises = """
//VERSION=3
const PARAMS = {
  // Indices
  chlIndex: 'default',
  tssIndex: 'default',
  watermaskIndices: ['ndwi', 'hol'],
  // Limits
  chlMin: -0.001,
  chlMax: 0.05,
  tssMin: 0.075,
  tssMax: 0.185,
  waterMax: -1,
  cloudMax: 0.02,
  // Graphics
  foreground: 'default',
  foregroundOpacity: 1.0,
  background: 'default',
  backgroundOpacity: 1.0
};
//* PARAMS END

/**
 * Returns indices object used for output calculation
 * The returned object is different for Sentinel-2 and Sentinel-3 satellites
  * Here only defined as strings and gets evaluated only when really needed
 * (Tip 4: Calculate as needed at https://medium.com/sentinel-hub/custom-scripts-faster-cheaper-better-83f73894658a)
 * natural: natural (rgb) color image
 * chl: chlorophyll indices
 * tss: sediment indices
 * watermask: watermask indices *
 *
 * @param {boolean} isSentinel3: is it Sentinel-3 or not (=Sentinel-2)
 */
function getIndices(isSentinel3) {
  return isSentinel3 ? {
    natural: "[1.0*B07+1.4*B09-0.1*B14,1.1*B05+1.4*B06-0.2*B14,2.6*B04-B14*0.6]",
    chl: {
      flh: "B10-1.005*(B08+(B11-B08)*((0.681-0.665)/(0.708-0.665)))",
      rlh: "B11-B10-(B18-B10*((0.70875-0.68125)*1000.0))/((0.885-0.68125)*1000.0)",
      mci: "B11-((0.75375-0.70875)/(0.75375-0.68125))*B10-(1.0-(0.75375-0.70875)/(0.75375-0.68125))*B12"
    },
    tss: {
      b07: "B07",
      b11: "B11"
    },
    watermask: {
      ndwi: "(B06-B17)/(B06+B17)"
    }
  } : {
      natural: "[2.5*B04,2.5*B03,2.5*B02]",
      chl: {
        rlh: "B05-B04-(B07-B04*((0.705-0.665)*1000.0))/((0.783-0.665)*1000.0)",
        mci: "B05-((0.74-0.705)/(0.74-0.665))*B04-(1.0-(0.74-0.705)/(0.74-0.665))*B06"
      },
      tss: {
        b05: "B05"
      },
      watermask: {
        ndwi: "(B03-B08)/(B03+B08)"
      }
    };
}

/**
 * Blends between two layers
 * Uses https://pierre-markuse.net/2019/03/26/sentinel-3-data-visualization-in-eo-browser-using-a-custom-script/
 *
 * @param {Object} layer1: first (top) layer
 * @param {Object} layer2: second (bottom) layer
 * @param {number} opacity1: first layer opacity
 * @param {number} opacity2: second layer opacity
 */
function blend(layer1, layer2, opacity1, opacity2) {
  return layer1.map(function (num, index) {
    return (num / 100) * opacity1 + (layer2[index] / 100) * opacity2;
  });
}

/**
 * Returns an opacity (alpha) value between 0 and 100 for a given index based on min and max values
 *
 * @param {Object} index: selected index
 * @param {number} min: user defined minimum value
 * @param {number} max: user defined maximum value
 */
function getAlpha(index, min, max) {
  if (min + (max - min) / 2 < index) {
    return 100;
  }
  return index <= min ?
    0 :
    index >= max ?
      1 :
      100 * ((index - min / 2) / (max - min));
}

/**
 * Returns a color palette for chlorophyll or sediment index
 *
 * @param {String} type: palette type ('chl' for chlorophyll, 'tss' for sediment)
 * @param {Object} index: user selected index
 * @param {number} min: user defined minimum value
 * @param {number} max: user defined maximum value
 * @param {boolean} isSentinel3Flh: is it Sentinel3 && is 'flh' is the user selected chlorophyll index (only for 'chl' type)
 */
function getColors(type, index, min, max, isSentinel3Flh) {
  let colors, palette;
  switch (type) {
    case 'chl':
      palette = [
        [0.0034, 0.0142, 0.163], // #01042A (almost black blue)
        [0, 0.416, 0.306], // #006A4E (bangladesh green)
        [0.486, 0.98, 0], //#7CFA00 (dark saturated chartreuse)
        [0.9465, 0.8431, 0.1048], //#F1D71B (light washed yellow)
        [1, 0, 0] // #FF0000 (red)
      ];
      // In case of Sentinel-3 && 'flh' the palette has to be reversed and min and max values also needed to be adjusted
      if (isSentinel3Flh) {
        palette = palette.reverse();
        min = min * 10;
        max = max / 10;
      }
      colors = colorBlend(
        index,
        [min, min + (max - min) / 3, (min + max) / 2, max - (max - min) / 3, max],
        palette
      );
      break;
    case 'tss':
      palette = [
        [0.961, 0.871, 0.702], // #F5DEB3 (wheat)
        [0.396, 0.263, 0.129] // #654321 (dark brown)
      ];
      colors = colorBlend(
        index,
        [min, max],
        palette
      );
      break;
    default:
      break;
  }
  return colors;
}

/**
 * Returns true if the pixel covers area of pure water without any cloud, shadow or snow, otherwise returns false
 * Based on the algorithm by Hollstein et al. at https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/hollstein/
 *
 * @param {boolean} isSentinel3: is it Sentinel-3 or not (=Sentinel-2)
 */
function isPureWater(isSentinel3) {
  return isSentinel3 ?
    B06 < 0.319 && B17 < 0.166 && B06 - B16 >= 0.027 && B20 - B21 < 0.021 :
    B03 < 0.319 && B8A < 0.166 && B03 - B07 >= 0.027 && B09 - B11 < 0.021;
}

/**
 * Returns whether the pixel is marked as cloud
 * Based on the algorithm by the Braaten-Cohen-Yang cloud detector at https://github.com/sentinel-hub/custom-scripts/tree/master/sentinel-2/cby_cloud_detection
 *
 * @param {number} limit: user defined cloud limit
 * @param {boolean} isSentinel3: is it Sentinel-3 or not (=Sentinel-2)
 */
function isCloud(limit, isSentinel3) {
  const bRatio = isSentinel3 ? (B04 - 0.175) / (0.39 - 0.175) : (B02 - 0.175) / (0.39 - 0.175);
  return bRatio > 1 || (bRatio > 0 && (B04 - B06) / (B04 + B06) > limit);
}

/**
 * Returns an evaluated code of a string
 * This was needed because functions with eval() won't make it through minification
 *
 * @param {String} s: input string to evaluate
 */
function getEval(s) {
  return eval(s);
}

/**
 * Returns whether the pixel is marked as water (not land, cloud or snow) based on the array of indices given by the user
 *
 * @param {Object} params: user defined parameters
 * @param {Array<String>} indices: array of water indices given by the user. Possible values: "ndwi", "hol", "bcy" and any of their combinations.
 * @param {boolean} isSentinel3: is it Sentinel-3 or not (=Sentinel-2)
 */
function isWater(availableWatermaskIndices, selectedWatermaskIndices, waterMax, cloudMax, isSentinel3) {
  if (selectedWatermaskIndices.length === 0) {
    return true;
  } else {
    let isItWater = true;
    for (let i = 0; i < selectedWatermaskIndices.length; i++) {
      const wm = selectedWatermaskIndices[i];
      if (wm == "ndwi" && getEval(availableWatermaskIndices.ndwi) < waterMax) {
        isItWater = false;
        break;
      } else if (wm == "hol" && !isPureWater(isSentinel3)) {
        isItWater = false;
        break;
      } else if (wm == "bcy" && isCloud(cloudMax, isSentinel3)) {
        isItWater = false;
        break;
      }
    }
    return isItWater;
  }
}

/**
 * Returns background layer
 *
 * @param {String | Array<number>} background: predefined or custom background color
 * @param {Array<numer>} naturalIndex: natural color index
 * @param {number} opacity: background opacity from 0 to 1 (floating value)
 */
function getBackground(background, naturalIndex, opacity) {
  let backgroundLayer;
  let isRgb = false;
  const alpha = parseInt(opacity * 100);
  // Default should be the natural layer
  if (background === 'default' || background === 'natural') {
    backgroundLayer = getEval(naturalIndex);
    isRgb = true;
  } else if (background === 'black') {
    // Black background
    backgroundLayer = [0, 0, 0];
  } else if (background === 'white') {
    // White background
    backgroundLayer = [1, 1, 1];
  } else {
    // Custom rgb colors array (eg. [255, 255, 0])
    backgroundLayer = getStaticColor(background);
  }
  // Only calculate alpha is really needed
  return isRgb || opacity === 1 ? backgroundLayer : blend(backgroundLayer, getEval(naturalIndex), alpha, 100 - alpha);
}

/**
 * Returns foreground layer
 *
 * @param {String | Array<number>} foreground: predefined or custom foreground color
 * @param {*} backgroundLayer: background layer (for blending)
 * @param {*} naturalIndex: natural layer
 * @param {*} opacity: foreground opacity from 0 to 1 (floating value)
 */
function getForeground(foreground, backgroundLayer, naturalIndex, opacity) {
  let layer;
  const alpha = parseInt(opacity * 100);
  if (foreground === 'natural') {
    layer = getEval(naturalIndex);
  } else {
    layer = getStaticColor(foreground);
  }
  return opacity === 1 ? layer : blend(layer, backgroundLayer, alpha, 100 - alpha);
}

/**
 * Transforms RGB 0-255 colors to 0.0-1.0
 *
 * @param {[number, number, number]} colorArray: 3-element array of RGB colors (0-255)
 */
function getStaticColor(colorArray) {
  return [colorArray[0] / 255, colorArray[1] / 255, colorArray[2] / 255];
}

/**
 * Runs the main calculation and returns the value for each pixel
 *
 * @param {Object} params: user defined parameters
 */
function getValue(params) {
  let chlIndex, chlLayer, tssIndex, tssLayer, tssAlpha;
  const chl = params.chlIndex;
  const tss = params.tssIndex;
  const background = params.background;
  const foreground = params.foreground;
  const foregroundOpacity = params.foregroundOpacity;
  // Decide whether the data is Sentinel-3 (otherwise it is assumed to be Sentinel-2)
  const isSentinel3 = typeof B18 !== "undefined";
  // Get the indices that could potentially be used
  const indices = getIndices(isSentinel3);
  // Define background layer
  const backgroundLayer = getBackground(background, indices.natural, params.backgroundOpacity);
  // Decide whether the pixel can be assumed as water
  // Return background layer if it is not water
  if (!isWater(indices.watermask, params.watermaskIndices, params.waterMax, params.cloudMax, isSentinel3)) {
    return backgroundLayer;
  }
  // Return a static color if set so with opacity
  if (foreground !== 'default') {
    return getForeground(foreground, backgroundLayer, indices.natural, foregroundOpacity);
  }
  let value;
  // Define the chlorophyll layer if needed
  if (chl !== null) {
    // In case of 'default' set proper algorighm
    const alg = chl === 'default' ? (isSentinel3 ? 'flh' : 'mci') : chl;
    chlIndex = getEval(indices.chl[alg]);
    chlLayer = getColors('chl', chlIndex, params.chlMin, params.chlMax, (isSentinel3 && alg === 'flh'));
  }
  // Define the sediment layer if needed
  if (tss !== null) {
    // In case of 'default' set proper algorighm
    const alg = tss === 'default' ? (isSentinel3 ? 'b11' : 'b05') : tss;
    tssIndex = getEval(indices.tss[alg]);
    tssLayer = getColors('tss', tssIndex, params.tssMin, params.tssMax);
    tssAlpha = getAlpha(tssIndex, params.tssMin, params.tssMax);
  }
  // Calculate output value
  if (chl !== null && tss !== null) {
    // Blend layers if both chlorophyll and sediment layers are requested
    // Put sediment layer on top of chlorophyll layer with alpha
    value = blend(tssLayer, chlLayer, tssAlpha, 100 - tssAlpha);
  } else if (chl !== null && tss === null) {
    // Chlorophyll layer only if sediment layer is null
    value = chlLayer;
  } else if (tss !== null && chl === null) {
    // Sediment layer only if chlorophyll layer is null
    // Put sediment layer on top of natural layer with alpha
    value = blend(tssLayer, backgroundLayer, tssAlpha, 100 - tssAlpha);
  } else {
    // Natural color layer if both chlorophyll and sediment layers are null (which does not make much sense)
    value = backgroundLayer;
  }
  // Return foreground (with opacity if needed on top of background)
  const foregroundAlpha = parseInt(foregroundOpacity * 100);
  return foregroundOpacity === 1 ? value : blend(value, backgroundLayer, foregroundAlpha, 100 - foregroundAlpha);
}

return getValue(PARAMS);
"""

evalscript_WQS = """
/*
Name:    Sentinel-2 Water Quality (Se2WaQ) 
Version: 1.0
Date:    2020-01-31

Author:      Nuno Sidónio Andrade Pereira
Affiliation: Polytechnic Institute of Beja, Portugal
License:     Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

Refs.: [1]M. Potes et al., “Use of Sentinel 2 – MSI for water quality 
          monitoring at Alqueva reservoir, Portugal,” Proc. Int. Assoc. 
          Hydrol. Sci., vol. 380, pp. 73–79, Dec. 2018.

       [2]K. Toming, T. Kutser, A. Laas, M. Sepp, B. Paavel, and T. Nõges,
          “First Experiences in Mapping Lake Water Quality Parameters with
          Sentinel-2 MSI Imagery,” Remote Sens., vol. 8, no. 8, p. 640, 
          Aug. 2016.
*/

// user defined FLAGs

var FLAGparam = 5;
var FLAGbackGround = 2;

// Water-land contrast index (to define the background)

var NDWI = index(B03, B08); 

// Background indexes                           

var Black = [0];                                       // FLAGbackGround = 0

var NDVI = index(B08, B04);                            // FLAGbackGround = 1

var TrueColor = [B04*2.5, B03*2.5, B02*2.5];           // FLAGbackGround = 2


// Empirical models

var Chl_a = 4.26 * Math.pow(B03/B01, 3.94);            // FLAGparam = 0; S2-L2A; [1] Unit: mg/m3;        

var Cya = 115530.31 * Math.pow(B03 * B04 / B02, 2.38); // FLAGparam = 1; S2-L2A; [1] Unit: 10^3 cell/ml; 

var Turb = 8.93 * (B03/B01) - 6.39;                    // FLAGparam = 2; S2-L2A; [1] Unit: NTU;          

var CDOM = 537 * Math.exp(-2.93*B03/B04);              // FLAGparam = 3; S2-L1C; [2] Unit: mg/l;         

var DOC = 432 * Math.exp(-2.24*B03/B04);               // FLAGparam = 4; S2-L1C; [2] Unit: mg/l;         

var Color = 25366 * Math.exp(-4.53*B03/B04);           // FLAGparam = 5; S2-L1C; [2] Unit: mg.Pt/l;      


// Numerical values for the scales of parameters

var scaleChl_a = [0, 6, 12, 20, 30, 50];
var scaleCya   = [0, 10, 20, 40, 50, 100];
var scaleTurb  = [0, 4, 8, 12, 16, 20];
var scaleCDOM  = [0, 1, 2, 3, 4, 5];
var scaleDOC   = [0, 5, 10, 20, 30, 40];
var scaleColor = [0, 10, 20, 30, 40, 50];

// Colors for the scales

var s = 255;
var colorScale = 
  [
   [73/s, 111/s, 242/s],
   [130/s, 211/s, 95/s],
   [254/s, 253/s, 5/s],
   [253/s, 0/s, 4/s],
   [142/s, 32/s, 38/s],
   [217/s, 124/s, 245/s]
  ];

// Image generation

if (NDWI<0) {
  if ( FLAGbackGround == 0 ) {
    return Black;
  } else if ( FLAGbackGround == 1 ) {
    return [0, .5*(NDVI+1), 0];
  } else if ( FLAGbackGround == 2 ) {
    return TrueColor;
  }
} else {
  switch ( FLAGparam ) {
    case 0:
     return colorBlend(Chl_a, scaleChl_a, colorScale);
     break;
    case 1:
      return colorBlend(Cya, scaleCya, colorScale);
      break;
    case 2:
      return colorBlend(Turb, scaleTurb, colorScale);
      break;
    case 3:
      return colorBlend(CDOM, scaleCDOM, colorScale);
      break;
    case 4:
      return colorBlend(DOC, scaleDOC, colorScale);
      break;
    case 5:
      return colorBlend(Color, scaleColor, colorScale);
      break;
    default:
      return TrueColor;
  }
}
"""