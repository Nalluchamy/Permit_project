const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const QRCode = require('qrcode');

/**
 * Generates a PDF permit based on the provided JSON data.
 * @param {Object} data - The permit JSON data
 * @param {string} outputPath - Where to save the generated PDF
 */
async function generatePermitPDF(data, outputPath) {
    console.log(`Generating professional permit for Serial: ${data.serial_no}...`);

    try {
        // 1. Generate QR Code Data URL (Base64)
        const baseUrl = "https://cheery-sherbet-91f7c4.netlify.app/";
        const params = new URLSearchParams({
            serial: data.serial_no || '',
            slip: data.dispatch_slip || '',
            minecode: data.minecode || '',
            date: `${data.traveling_date || ''} ${data.traveling_time || ''}`,
            vehicle: data.vehicle_no || '',
            mineral: `${data.mineral || ''}(${data.quantity || '0'}MT)`,
            distance: data.distance || '',
            reqtime: data.req_hours || '',
            dest: data.destination || ''
        });
        
        const qrDataUrl = await QRCode.toDataURL(baseUrl + '?' + params.toString(), {
            errorCorrectionLevel: 'M',
            margin: 1,
            width: 150
        });

        // 2. Read HTML Template
        const templatePath = path.join(__dirname, 'template.html');
        let htmlTemplate = fs.readFileSync(templatePath, 'utf8');

        // 3. Inject Data into Template
        // Add calculated/derived fields
        const templateData = {
            ...data,
            qr_code_url: qrDataUrl,
            dispatch_datetime: new Date().toLocaleString('en-IN', { hour12: false })
        };

        // Simple string replacement for {{key}} tags
        for (const [key, value] of Object.entries(templateData)) {
            const regex = new RegExp(`{{${key}}}`, 'g');
            htmlTemplate = htmlTemplate.replace(regex, value || '');
        }

        // Clean up any remaining unresolved tags if necessary
        htmlTemplate = htmlTemplate.replace(/{{[a-zA-Z0-9_]+}}/g, '');

        // 4. Launch Puppeteer to render HTML to PDF
        const browser = await puppeteer.launch({ 
            // headless: "new" is recommended, we use default for simplicity
            args: ['--no-sandbox', '--disable-setuid-sandbox'] 
        });
        
        const page = await browser.newPage();
        
        // Set content and wait for network idle to ensure fonts/images are loaded
        await page.setContent(htmlTemplate, { waitUntil: 'networkidle0' });

        // Generate PDF
        await page.pdf({
            path: outputPath,
            format: 'A4',
            printBackground: true, // Required to print CSS backgrounds and borders
            margin: {
                top: '0mm',
                right: '0mm',
                bottom: '0mm',
                left: '0mm'
            }
        });

        await browser.close();
        console.log(`✅ Success! PDF saved to: ${outputPath}`);

    } catch (error) {
        console.error('❌ Error generating PDF:', error);
    }
}

// ------ EXAMPLE USAGE ------ //
const sampleData = {
    serial_no: "TN03996631",
    dispatch_slip: "DISP000007354833",
    minecode: "KKIN0025",
    traveling_date: "01-04-2028 07:48 pm",
    traveling_time: "", // Handled in traveling_date for sample
    hsn_code: "6290009",
    lessee_id: "CHN241557",
    lessee_name: "Gautham P M",
    lessee_address: "No. 19, 11th Avenue, Ashok nagar, Chennai - 600083",
    district: "Kallakurichi",
    taluk: "Ulundurpet",
    village: "Kallamedu",
    sf_no: "58/1 (P-1)., / 00002.85.00",
    mineral: "Pebbles",
    bulk_permit: "KK/2600000085",
    order_ref: "ORD-99221",
    classification: "Porampoke Land",
    lease_period: "12-07-2024 to 07-11-2028",
    within_tn: "Yes",
    delivered_to: "MANI",
    vehicle_no: "TN58J7212",
    vehicle_type: "Taurus 19",
    distance: "689",
    destination: "ARANTHANGI, PIN-638001, TAMIL NADU",
    via: "THANJAVUR",
    req_hours: "12hrs (02-04-2028 07:48 am)",
    quantity: "9",
    driver_name: "PARAMASIVAM",
    driver_license: "TN31Y20090003199",
    driver_phone: "9642063599",
    auth_person: "Gautham P M"
};

// Run if called directly
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length >= 1) {
        // Mode 1: Called from Python with a JSON file
        // Usage: node generate.js <data.json> [output.pdf]
        const dataPath = args[0];
        const outPath = args[1] || path.join(__dirname, 'Sample_Permit.pdf');
        
        try {
            const dataString = fs.readFileSync(dataPath, 'utf8');
            const data = JSON.parse(dataString);
            generatePermitPDF(data, outPath).then(() => {
                // Optionally clean up the temp json if needed, 
                // but usually the caller handles the temp file.
            });
        } catch (err) {
            console.error("❌ Failed to parse input JSON or generate PDF:", err);
            process.exit(1);
        }
    } else {
        // Mode 2: Sample run (for testing)
        const outPath = path.join(__dirname, 'Sample_Permit.pdf');
        generatePermitPDF(sampleData, outPath);
    }
}

module.exports = { generatePermitPDF };
